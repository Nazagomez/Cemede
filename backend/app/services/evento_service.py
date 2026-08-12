"""Environmental event notification and approval helpers."""

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.enums import EstadoEvento, OrigenEvento, RolUsuario, TipoAvisoPublico
from app.models import EventoAmbiental, Usuario
from app.services.aviso_service import create_public_aviso
from app.services.notificacion_service import (
    create_event_approved_notifications,
    create_event_closed_notifications,
    create_pending_event_admin_notifications,
)

EVENTO_PENDIENTE_AVISO_TITULO = "Evento ambiental en revisión"
EVENTO_APROBADO_AVISO_TITULO = "Evento ambiental activo"
EVENTO_CERRADO_AVISO_TITULO = "Evento ambiental cerrado"


def resolve_evento_origen(current_user: Usuario | None) -> OrigenEvento:
    """Map authenticated user role to event origin."""
    if current_user is None:
        return OrigenEvento.VISITANTE
    if current_user.rol == RolUsuario.ADMINISTRADOR:
        return OrigenEvento.ADMINISTRADOR
    return OrigenEvento.INVESTIGADOR


def notify_evento_pendiente(
    db: Session,
    evento: EventoAmbiental,
    playa_nombre: str,
) -> None:
    """Notify administrators and publish a public pending announcement."""
    create_pending_event_admin_notifications(db, evento, playa_nombre)
    create_public_aviso(
        db=db,
        evento_id=evento.id,
        playa_id=evento.playa_id,
        titulo=EVENTO_PENDIENTE_AVISO_TITULO,
        mensaje=f"Se reportó {evento.tipo.value} en {playa_nombre}. Pendiente de aprobación.",
        tipo=TipoAvisoPublico.EVENTO_PENDIENTE,
    )


def notify_evento_aprobado(
    db: Session,
    evento: EventoAmbiental,
    playa_nombre: str,
    factor_correccion: float,
) -> None:
    """Notify all active users and publish a public approved announcement."""
    create_event_approved_notifications(db, evento, playa_nombre, factor_correccion)
    create_public_aviso(
        db=db,
        evento_id=evento.id,
        playa_id=evento.playa_id,
        titulo=EVENTO_APROBADO_AVISO_TITULO,
        mensaje=(
            f"Se aprobó {evento.tipo.value} en {playa_nombre}. "
            f"Factor de corrección = {factor_correccion:.4f}."
        ),
        tipo=TipoAvisoPublico.EVENTO_APROBADO,
    )


def notify_evento_cerrado(
    db: Session,
    evento: EventoAmbiental,
    playa_nombre: str,
) -> None:
    """Notify all active users and publish a public closed announcement."""
    create_event_closed_notifications(db, evento, playa_nombre)
    create_public_aviso(
        db=db,
        evento_id=evento.id,
        playa_id=evento.playa_id,
        titulo=EVENTO_CERRADO_AVISO_TITULO,
        mensaje=f"Se cerró {evento.tipo.value} en {playa_nombre}.",
        tipo=TipoAvisoPublico.EVENTO_CERRADO,
    )


def ensure_evento_is_pending(evento: EventoAmbiental) -> None:
    """Validate that an event is still pending approval."""
    if evento.estado != EstadoEvento.PENDIENTE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Solo se pueden revisar eventos pendientes",
        )


def ensure_evento_is_approved(evento: EventoAmbiental) -> None:
    """Validate that an event is approved and still active."""
    if evento.estado != EstadoEvento.APROBADO or not evento.activo:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Solo se pueden cerrar eventos aprobados y activos",
        )
