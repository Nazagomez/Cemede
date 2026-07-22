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


def get_stored_factors_by_evento(db: Session, evento_ids: list[int]) -> dict[int, float]:
    """Return persisted correction factors keyed by event id."""
    if not evento_ids:
        return {}
    factores = db.query(FactorCorreccion).filter(FactorCorreccion.evento_id.in_(evento_ids)).all()
    return {factor.evento_id: float(factor.valor) for factor in factores}


def resolve_factor_correccion(evento: EventoAmbiental, stored_factors: dict[int, float]) -> float:
    """Return persisted factor when available, otherwise compute from magnitudes."""
    stored_factor = stored_factors.get(evento.id)
    if stored_factor is not None:
        return stored_factor
    return calcular_factor_correccion(float(evento.parte_afectada), float(evento.totalidad_analizada))


def obtener_eventos_activos(db: Session, playa_id: int) -> list[EventoAmbiental]:
    """Return active environmental events for a beach."""
    return (
        db.query(EventoAmbiental)
        .filter(EventoAmbiental.playa_id == playa_id, EventoAmbiental.activo.is_(True))
        .all()
    )


def obtener_factores_activos(db: Session, playa_id: int) -> list[float]:
    """Get correction factors applied to active environmental events."""
    eventos = obtener_eventos_activos(db, playa_id)
    if not eventos:
        return []
    stored_factors = get_stored_factors_by_evento(db, [evento.id for evento in eventos])
    return [resolve_factor_correccion(evento, stored_factors) for evento in eventos]


def build_eventos_activos_resumen(db: Session, playa_id: int) -> list[dict[str, float | int | str]]:
    """Build dashboard summary for active events using the same factors as CCR."""
    eventos = obtener_eventos_activos(db, playa_id)
    if not eventos:
        return []
    stored_factors = get_stored_factors_by_evento(db, [evento.id for evento in eventos])
    return [
        {
            "id": evento.id,
            "tipo": evento.tipo.value,
            "titulo": evento.titulo,
            "factor_correccion": resolve_factor_correccion(evento, stored_factors),
        }
        for evento in eventos
    ]


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
