"""Visitor registration business logic."""

from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from app.models import RegistroVisitante


def cerrar_visitas_vencidas(db: Session) -> None:
    """Auto-close visitor records whose estimated stay has already elapsed.

    Runs lazily whenever visitor data is read (occupancy, capacity,
    history) instead of a background job: any record with
    ``duracion_estimada_horas`` set and no ``fecha_salida`` gets closed
    at its estimated exit time once that moment has passed.
    """
    ahora = datetime.utcnow()
    candidatos = (
        db.query(RegistroVisitante)
        .filter(
            RegistroVisitante.fecha_salida.is_(None),
            RegistroVisitante.duracion_estimada_horas.isnot(None),
        )
        .all()
    )
    hubo_cambios = False
    for registro in candidatos:
        fecha_estimada_salida = registro.fecha_entrada + timedelta(
            hours=float(registro.duracion_estimada_horas)
        )
        if ahora >= fecha_estimada_salida:
            registro.fecha_salida = fecha_estimada_salida
            hubo_cambios = True
    if hubo_cambios:
        db.commit()