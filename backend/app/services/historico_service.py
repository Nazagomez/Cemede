"""Historical visitation import and capacity estimation backfill."""

from datetime import datetime
from pathlib import Path

from openpyxl import load_workbook
from sqlalchemy.orm import Session

from app.constants.ccf_field_params import CEMEDE_FIELD_CCF_PARAMS
from app.enums import MetodoCcr
from app.models import ConfiguracionCcf, EstimacionCapacidad, Playa, VisitacionHistorica
from app.services.capacidad_service import (
    calcular_ccf,
    calcular_cce,
    calcular_ccr,
    calcular_porcentaje_ocupacion,
)

SITIO_PLAYA_KEYWORDS: list[tuple[str, str]] = [
    ("junquillal", "junquillal"),
    ("baulas", "playa_grande"),
    ("playa grande", "playa_grande"),
]


def resolve_playa_id_from_sitio(db: Session, sitio: str) -> int | None:
    """Map Excel site label to playa id using name keywords."""
    sitio_lower = sitio.strip().lower()
    for keyword, field_key in SITIO_PLAYA_KEYWORDS:
        if keyword in sitio_lower:
            params = CEMEDE_FIELD_CCF_PARAMS[field_key]
            playa = db.query(Playa).filter(Playa.nombre == params.playa_nombre).first()
            if playa is not None:
                return playa.id
    playas = db.query(Playa).all()
    for playa in playas:
        if playa.nombre.lower() in sitio_lower or sitio_lower in playa.nombre.lower():
            return playa.id
    return None


def _normalize_header(value: object) -> str:
    """Normalize spreadsheet header names."""
    if value is None:
        return ""
    normalized = str(value).strip().lower()
    for source, target in (("á", "a"), ("é", "e"), ("í", "i"), ("ó", "o"), ("ú", "u"), ("ñ", "n")):
        normalized = normalized.replace(source, target)
    if normalized == "ano":
        return "anio"
    return normalized


def import_visitacion_from_excel(db: Session, excel_path: str) -> dict[str, int]:
    """Load visitation workbook rows into visitacion_historica."""
    path = Path(excel_path)
    if not path.is_file():
        raise FileNotFoundError(f"No se encontró el archivo Excel: {excel_path}")
    workbook = load_workbook(path, read_only=True, data_only=True)
    sheet = workbook[workbook.sheetnames[0]]
    rows = sheet.iter_rows(values_only=True)
    headers = [_normalize_header(value) for value in next(rows)]
    column_index = {header: index for index, header in enumerate(headers) if header}
    required = {"anio", "sitio", "tipo_visitante", "cantidad_visitas"}
    if not required.issubset(column_index.keys()):
        raise ValueError("El Excel no contiene las columnas requeridas: anio, sitio, tipo_visitante, cantidad_visitas")
    inserted = 0
    updated = 0
    for row in rows:
        if row is None or all(cell is None for cell in row):
            continue
        sitio = str(row[column_index["sitio"]]).strip()
        playa_id = resolve_playa_id_from_sitio(db, sitio)
        if playa_id is None:
            continue
        anio = int(row[column_index["anio"]])
        tipo_visitante = str(row[column_index["tipo_visitante"]]).strip()
        cantidad_raw = row[column_index["cantidad_visitas"]]
        cantidad_visitas = int(cantidad_raw) if cantidad_raw is not None else 0
        calidad = row[column_index.get("calidad_dato", -1)] if "calidad_dato" in column_index else None
        fuente = row[column_index.get("fuente", -1)] if "fuente" in column_index else None
        url_fuente = row[column_index.get("url_fuente", -1)] if "url_fuente" in column_index else None
        observacion = row[column_index.get("observacion", -1)] if "observacion" in column_index else None
        existing = (
            db.query(VisitacionHistorica)
            .filter(
                VisitacionHistorica.playa_id == playa_id,
                VisitacionHistorica.anio == anio,
                VisitacionHistorica.tipo_visitante == tipo_visitante,
            )
            .first()
        )
        if existing is None:
            db.add(
                VisitacionHistorica(
                    playa_id=playa_id,
                    anio=anio,
                    tipo_visitante=tipo_visitante,
                    cantidad_visitas=cantidad_visitas,
                    calidad_dato=str(calidad) if calidad is not None else None,
                    fuente=str(fuente) if fuente is not None else None,
                    url_fuente=str(url_fuente) if url_fuente is not None else None,
                    observacion=str(observacion) if observacion is not None else None,
                )
            )
            inserted += 1
        else:
            existing.cantidad_visitas = cantidad_visitas
            existing.calidad_dato = str(calidad) if calidad is not None else None
            existing.fuente = str(fuente) if fuente is not None else None
            existing.url_fuente = str(url_fuente) if url_fuente is not None else None
            existing.observacion = str(observacion) if observacion is not None else None
            updated += 1
    db.flush()
    return {"inserted": inserted, "updated_or_skipped": updated}


def _fecha_calculo_from_record(anio: int, tipo_visitante: str) -> datetime:
    """Build a stable timestamp per historical row."""
    month = 1 if tipo_visitante.lower().startswith("residente") else 7
    return datetime(anio, month, 15, 12, 0, 0)


def _visitantes_from_annual_count(cantidad_visitas: int) -> int:
    """Convert annual visits to an average daily occupancy proxy."""
    if cantidad_visitas <= 0:
        return 0
    return max(1, int(round(cantidad_visitas / 365)))


def sync_config_from_field_params(db: Session) -> int:
    """Align configuracion_ccf with CEMEDE field-validated parameters."""
    updated = 0
    playas = db.query(Playa).all()
    for playa in playas:
        field_key = None
        for key, params in CEMEDE_FIELD_CCF_PARAMS.items():
            if params.playa_nombre == playa.nombre:
                field_key = key
                break
        if field_key is None:
            continue
        params = CEMEDE_FIELD_CCF_PARAMS[field_key]
        config = db.query(ConfiguracionCcf).filter(ConfiguracionCcf.playa_id == playa.id).first()
        if config is None:
            continue
        config.area_por_visitante_m2 = params.area_por_visitante_m2
        config.periodo_horas = params.periodo_horas
        config.tiempo_permanencia_horas = params.tiempo_permanencia_horas
        config.capacidad_manejo = params.capacidad_manejo
        playa.area_util_m2 = params.area_util_m2
        updated += 1
    db.flush()
    return updated


def generate_estimaciones_from_visitacion(db: Session, playa_id: int | None = None) -> dict[str, int]:
    """Create estimacion_capacidad rows from imported visitation history."""
    query = db.query(VisitacionHistorica)
    if playa_id is not None:
        query = query.filter(VisitacionHistorica.playa_id == playa_id)
    registros = query.order_by(VisitacionHistorica.anio.asc()).all()
    created = 0
    refreshed = 0
    for registro in registros:
        playa = db.query(Playa).filter(Playa.id == registro.playa_id).first()
        config = db.query(ConfiguracionCcf).filter(ConfiguracionCcf.playa_id == registro.playa_id).first()
        if playa is None or config is None:
            continue
        fecha_calculo = _fecha_calculo_from_record(registro.anio, registro.tipo_visitante)
        existing = (
            db.query(EstimacionCapacidad)
            .filter(
                EstimacionCapacidad.playa_id == registro.playa_id,
                EstimacionCapacidad.fecha_calculo == fecha_calculo,
            )
            .first()
        )
        ccf = calcular_ccf(
            float(playa.area_util_m2),
            float(config.area_por_visitante_m2),
            float(config.periodo_horas),
            float(config.tiempo_permanencia_horas),
        )
        ccr_formula = calcular_ccr(ccf, [1.0])
        visitantes = _visitantes_from_annual_count(registro.cantidad_visitas)
        porcentaje = calcular_porcentaje_ocupacion(visitantes, ccr_formula)
        cce = calcular_cce(ccr_formula, float(config.capacidad_manejo))
        if existing is None:
            db.add(
                EstimacionCapacidad(
                    playa_id=registro.playa_id,
                    fecha_calculo=fecha_calculo,
                    ccf=ccf,
                    ccr_formula=ccr_formula,
                    ccr_ml=None,
                    ccr_final=ccr_formula,
                    cce=cce,
                    visitantes_actuales=visitantes,
                    porcentaje_ocupacion=porcentaje,
                    eventos_activos=0,
                    metodo_ccr=MetodoCcr.FORMULA,
                )
            )
            created += 1
        else:
            existing.ccf = ccf
            existing.ccr_formula = ccr_formula
            existing.ccr_final = ccr_formula
            existing.cce = cce
            existing.visitantes_actuales = visitantes
            existing.porcentaje_ocupacion = porcentaje
            existing.eventos_activos = 0
            existing.metodo_ccr = MetodoCcr.FORMULA
            refreshed += 1
    db.flush()
    return {"created": created, "refreshed": refreshed, "total_source_rows": len(registros)}
