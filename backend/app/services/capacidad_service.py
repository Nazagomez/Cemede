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
