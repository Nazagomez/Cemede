"""Notification business logic."""

from sqlalchemy.dialects.mysql import insert as mysql_insert
from sqlalchemy.orm import Session

from app.enums import RolUsuario
from app.models import EventoAmbiental, Notificacion, Playa, Usuario
from app.schemas import NotificacionResponse

EVENTO_PENDIENTE_TITLE = "Evento pendiente de aprobación"
EVENTO_APROBADO_TITLE = "Evento ambiental aprobado"
EVENTO_CERRADO_TITLE = "Evento ambiental cerrado"
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
    return list_notifications(db, leida=leida, usuario_id=usuario_id)


def list_notifications(
    db: Session,
    leida: bool | None = None,
    usuario_id: int | None = None,
    playa_id: int | None = None,
) -> list[NotificacionResponse]:
    """List notifications with optional filters."""
    query = db.query(Notificacion, Playa.nombre).join(Playa, Playa.id == Notificacion.playa_id)
    if leida is not None:
        query = query.filter(Notificacion.leida.is_(leida))
    if usuario_id is not None:
        query = query.filter(Notificacion.usuario_id == usuario_id)
    if playa_id is not None:
        query = query.filter(Notificacion.playa_id == playa_id)
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
    create_event_approved_notifications(db, evento, playa_nombre, None)


def create_pending_event_admin_notifications(
    db: Session,
    evento: EventoAmbiental,
    playa_nombre: str,
) -> None:
    """Create a pending approval notification for every active administrator."""
    admin_ids = [
        admin_id
        for admin_id, in db.query(Usuario.id)
        .filter(Usuario.activo.is_(True), Usuario.rol == RolUsuario.ADMINISTRADOR)
        .all()
    ]
    notifications = [
        Notificacion(
            usuario_id=admin_id,
            evento_id=evento.id,
            playa_id=evento.playa_id,
            titulo=EVENTO_PENDIENTE_TITLE,
            mensaje=f"Hay un evento {evento.tipo.value} en {playa_nombre} pendiente de aprobación",
        )
        for admin_id in admin_ids
    ]
    db.add_all(notifications)


def create_event_approved_notifications(
    db: Session,
    evento: EventoAmbiental,
    playa_nombre: str,
    factor_correccion: float | None,
) -> None:
    """Create an approved event notification for every active user."""
    usuario_ids = [
        usuario_id
        for usuario_id, in db.query(Usuario.id).filter(Usuario.activo.is_(True)).all()
    ]
    factor_text = (
        f" Factor de corrección = {factor_correccion:.4f}."
        if factor_correccion is not None
        else ""
    )
    notifications = [
        Notificacion(
            usuario_id=usuario_id,
            evento_id=evento.id,
            playa_id=evento.playa_id,
            titulo=EVENTO_APROBADO_TITLE,
            mensaje=f"Se aprobó {evento.tipo.value} en {playa_nombre}.{factor_text}",
        )
        for usuario_id in usuario_ids
    ]
    db.add_all(notifications)


def create_event_closed_notifications(
    db: Session,
    evento: EventoAmbiental,
    playa_nombre: str,
) -> None:
    """Create a closed event notification for every active user."""
    usuario_ids = [
        usuario_id
        for usuario_id, in db.query(Usuario.id).filter(Usuario.activo.is_(True)).all()
    ]
    notifications = [
        Notificacion(
            usuario_id=usuario_id,
            evento_id=evento.id,
            playa_id=evento.playa_id,
            titulo=EVENTO_CERRADO_TITLE,
            mensaje=f"Se cerró {evento.tipo.value} en {playa_nombre}",
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
    usuario_ids = [
        usuario_id
        for usuario_id, in db.query(Usuario.id).filter(Usuario.activo.is_(True)).all()
    ]
    notification_values = [
        {
            "usuario_id": usuario_id,
            "playa_id": playa_id,
            "titulo": titulo,
            "mensaje": (
                f"La ocupación de {playa_nombre} alcanzó "
                f"{porcentaje_ocupacion:.2f}% ({estado})"
            ),
            "deduplication_key": f"occupancy:{usuario_id}:{playa_id}:{estado}",
        }
        for usuario_id in usuario_ids
    ]
    if notification_values:
        statement = mysql_insert(Notificacion).values(notification_values)
        statement = statement.on_duplicate_key_update(
            deduplication_key=statement.inserted.deduplication_key,
        )
        db.execute(statement)
