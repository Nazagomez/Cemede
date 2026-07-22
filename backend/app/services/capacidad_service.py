"""Carrying capacity calculation services (Cifuentes et al., 1999)."""

from datetime import datetime

from sqlalchemy.orm import Session

from app.enums import MetodoCcr
from app.models import ConfiguracionCcf, EstimacionCapacidad, EventoAmbiental, FactorCorreccion, Playa, RegistroVisitante


def calcular_factor_correccion(magnitud_limitante: float, magnitud_total: float) -> float:
    """Calculate FC = 1 - (Ml / Mt)."""
    if magnitud_total <= 0:
        return 1.0
    factor = 1 - (magnitud_limitante / magnitud_total)
    return round(max(factor, 0.0), 4)


def calcular_ccf(area_util: float, area_por_visitante: float, periodo_horas: float, tiempo_permanencia: float) -> float:
    """Calculate physical carrying capacity."""
    if area_por_visitante <= 0 or tiempo_permanencia <= 0:
        return 0.0
    nv = periodo_horas / tiempo_permanencia
    ccf = (area_util / area_por_visitante) * nv
    return round(ccf, 2)


def calcular_ccr(ccf: float, factores: list[float]) -> float:
    """Calculate real carrying capacity."""
    ccr = ccf
    for factor in factores:
        ccr *= factor
    return round(ccr, 2)


def calcular_cce(ccr: float, capacidad_manejo: float) -> float:
    """Calculate effective carrying capacity."""
    return round(ccr * capacidad_manejo, 2)


def obtener_visitantes_activos(db: Session, playa_id: int) -> int:
    """Count active visitors for a beach."""
    registros = (
        db.query(RegistroVisitante)
        .filter(RegistroVisitante.playa_id == playa_id, RegistroVisitante.fecha_salida.is_(None))
        .all()
    )
    return sum(registro.cantidad_personas for registro in registros)


def obtener_factores_activos(db: Session, playa_id: int) -> list[float]:
    """Get persisted correction factors from active environmental events."""
    eventos = (
        db.query(EventoAmbiental)
        .filter(EventoAmbiental.playa_id == playa_id, EventoAmbiental.activo.is_(True))
        .all()
    )
    if not eventos:
        return []
    evento_ids = [evento.id for evento in eventos]
    stored_factors = {
        factor.evento_id: float(factor.valor)
        for factor in db.query(FactorCorreccion).filter(FactorCorreccion.evento_id.in_(evento_ids)).all()
    }
    return [stored_factors[evento.id] for evento in eventos if evento.id in stored_factors]


def calcular_estado_ocupacion(porcentaje: float) -> str:
    """Map occupancy percentage to status."""
    if porcentaje < 70:
        return "normal"
    if porcentaje <= 90:
        return "advertencia"
    return "critico"


def calcular_porcentaje_ocupacion(visitantes: int, ccr_formula: float) -> float:
    """Calculate occupancy percentage."""
    if ccr_formula <= 0:
        return 100.0 if visitantes > 0 else 0.0
    return round((visitantes / ccr_formula) * 100, 2)


def construir_estimacion(
    db: Session,
    playa: Playa,
    config: ConfiguracionCcf,
    guardar: bool = False,
) -> dict[str, float | int | str | datetime | None]:
    """Build full capacity estimation for a beach."""
    fecha_calculo = datetime.utcnow()
    ccf = calcular_ccf(
        float(playa.area_util_m2),
        float(config.area_por_visitante_m2),
        float(config.periodo_horas),
        float(config.tiempo_permanencia_horas),
    )
    factores = obtener_factores_activos(db, playa.id)
    ccr_formula = calcular_ccr(ccf, factores if factores else [1.0])
    cce = calcular_cce(ccr_formula, float(config.capacidad_manejo))
    visitantes = obtener_visitantes_activos(db, playa.id)
    porcentaje = calcular_porcentaje_ocupacion(visitantes, ccr_formula)
    eventos_activos = len(factores)
    estimacion_id: int | None = None
    if guardar:
        estimacion = EstimacionCapacidad(
            playa_id=playa.id,
            fecha_calculo=fecha_calculo,
            ccf=ccf,
            ccr_formula=ccr_formula,
            ccr_ml=None,
            ccr_final=ccr_formula,
            cce=cce,
            visitantes_actuales=visitantes,
            porcentaje_ocupacion=porcentaje,
            metodo_ccr=MetodoCcr.FORMULA,
        )
        db.add(estimacion)
        db.commit()
        db.refresh(estimacion)
        fecha_calculo = estimacion.fecha_calculo
        estimacion_id = estimacion.id
    return {
        "estimacion_id": estimacion_id,
        "fecha_calculo": fecha_calculo,
        "ccf": ccf,
        "ccr_formula": ccr_formula,
        "ccr_ml": None,
        "ccr_final": ccr_formula,
        "cce": cce,
        "metodo_ccr": MetodoCcr.FORMULA.value,
        "visitantes_actuales": visitantes,
        "porcentaje_ocupacion": porcentaje,
        "eventos_activos": eventos_activos,
        "estado": calcular_estado_ocupacion(porcentaje),
    }
