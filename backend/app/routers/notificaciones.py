"""Notification routes."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.database import get_db
from app.models import Notificacion, Usuario
from app.schemas import MessageResponse, NotificacionLeidaResponse, NotificacionResponse
from app.services.notificacion_service import list_notifications

router = APIRouter(prefix="/notificaciones", tags=["Notificaciones"])


@router.get("", response_model=list[NotificacionResponse])
def get_notificaciones(
    leida: bool | None = None,
    playa_id: int | None = None,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
) -> list[NotificacionResponse]:
    """List the current user's notifications with optional filters."""
    return list_notifications(db, leida=leida, usuario_id=current_user.id, playa_id=playa_id)


@router.put("/leidas", response_model=MessageResponse)
def mark_all_as_read(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
) -> MessageResponse:
    """Mark all of the current user's unread notifications as read."""
    db.query(Notificacion).filter(
        Notificacion.usuario_id == current_user.id,
        Notificacion.leida.is_(False),
    ).update({"leida": True, "deduplication_key": None})
    db.commit()
    return MessageResponse(mensaje="Notificaciones marcadas como leídas")


@router.put("/{notificacion_id}/leida", response_model=NotificacionLeidaResponse)
def mark_notificacion_as_read(
    notificacion_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
) -> NotificacionLeidaResponse:
    """Mark one of the current user's notifications as read."""
    notificacion = (
        db.query(Notificacion)
        .filter(Notificacion.id == notificacion_id, Notificacion.usuario_id == current_user.id)
        .first()
    )
    if notificacion is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notificación no encontrada",
        )
    notificacion.leida = True
    notificacion.deduplication_key = None
    db.commit()
    return NotificacionLeidaResponse(id=notificacion.id, leida=notificacion.leida)