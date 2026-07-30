"""Notification business logic."""

from sqlalchemy.orm import Session

from app.models import Notificacion, Playa
from app.schemas import NotificacionResponse


def build_notificacion_response(
    notificacion: Notificacion,
    playa_nombre: str,
) -> NotificacionResponse:
    """Build a notification API response."""
    return NotificacionResponse(
        id=notificacion.id,
        evento_id=notificacion.evento_id,
        playa_id=notificacion.playa_id,
        playa_nombre=playa_nombre,
        titulo=notificacion.titulo,
        mensaje=notificacion.mensaje,
        leida=notificacion.leida,
        created_at=notificacion.created_at,
    )


def list_user_notifications(
    db: Session,
    usuario_id: int,
    leida: bool | None = None,
) -> list[NotificacionResponse]:
    """List a user's notifications with an optional read-status filter."""
    query = (
        db.query(Notificacion, Playa.nombre)
        .join(Playa, Playa.id == Notificacion.playa_id)
        .filter(Notificacion.usuario_id == usuario_id)
    )
    if leida is not None:
        query = query.filter(Notificacion.leida.is_(leida))
    rows = query.order_by(Notificacion.created_at.desc()).all()
    return [
        build_notificacion_response(notificacion, playa_nombre)
        for notificacion, playa_nombre in rows
    ]
