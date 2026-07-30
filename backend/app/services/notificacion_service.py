"""Notification business logic."""

from sqlalchemy.orm import Session

from app.models import EventoAmbiental, Notificacion, Playa, Usuario
from app.schemas import NotificacionResponse

EVENTO_NOTIFICATION_TITLE = "Evento ambiental reportado"
OCUPACION_ADVERTENCIA_TITLE = "Ocupación en advertencia"
OCUPACION_CRITICA_TITLE = "Ocupación crítica"

OCCUPANCY_NOTIFICATION_TITLES = {
    "advertencia": OCUPACION_ADVERTENCIA_TITLE,
    "critico": OCUPACION_CRITICA_TITLE,
}


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


def create_event_notifications(
    db: Session,
    evento: EventoAmbiental,
    playa_nombre: str,
) -> None:
    """Create an environmental event notification for every active user."""
    usuario_ids = [
        usuario_id
        for usuario_id, in db.query(Usuario.id).filter(Usuario.activo.is_(True)).all()
    ]
    notifications = [
        Notificacion(
            usuario_id=usuario_id,
            evento_id=evento.id,
            playa_id=evento.playa_id,
            titulo=EVENTO_NOTIFICATION_TITLE,
            mensaje=f"Se reportó {evento.tipo.value} en {playa_nombre}",
        )
        for usuario_id in usuario_ids
    ]
    db.add_all(notifications)


def create_occupancy_notifications(
    db: Session,
    playa_id: int,
    playa_nombre: str,
    estado: str,
    porcentaje_ocupacion: float,
) -> None:
    """Create one unread occupancy alert per active user and severity."""
    titulo = OCCUPANCY_NOTIFICATION_TITLES.get(estado)
    if titulo is None:
        return
    usuario_ids = {
        usuario_id
        for usuario_id, in db.query(Usuario.id).filter(Usuario.activo.is_(True)).all()
    }
    notified_user_ids = {
        usuario_id
        for usuario_id, in (
            db.query(Notificacion.usuario_id)
            .filter(
                Notificacion.playa_id == playa_id,
                Notificacion.titulo == titulo,
                Notificacion.leida.is_(False),
            )
            .all()
        )
    }
    pending_user_ids = usuario_ids - notified_user_ids
    notifications = [
        Notificacion(
            usuario_id=usuario_id,
            playa_id=playa_id,
            titulo=titulo,
            mensaje=(
                f"La ocupación de {playa_nombre} alcanzó "
                f"{porcentaje_ocupacion:.2f}% ({estado})"
            ),
        )
        for usuario_id in pending_user_ids
    ]
    db.add_all(notifications)
