"""Visitor occupancy helpers (phase 3)."""

from sqlalchemy.orm import Session

from app.models import RegistroVisitante


def obtener_visitantes_activos(db: Session, playa_id: int) -> int:
    """Count active visitors for a beach."""
    registros = (
        db.query(RegistroVisitante)
        .filter(RegistroVisitante.playa_id == playa_id, RegistroVisitante.fecha_salida.is_(None))
        .all()
    )
    return sum(registro.cantidad_personas for registro in registros)


def calcular_factor_correccion(magnitud_limitante: float, magnitud_total: float) -> float:
    """Calculate FC = 1 - (Ml / Mt)."""
    if magnitud_total <= 0:
        return 1.0
    factor = 1 - (magnitud_limitante / magnitud_total)
    return round(max(factor, 0.0), 4)
