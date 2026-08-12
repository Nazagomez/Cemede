"""Notification routes."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Notificacion
from app.schemas import NotificacionLeidaResponse, NotificacionResponse
from app.services.notificacion_service import list_notifications

router = APIRouter(prefix="/notificaciones", tags=["Notificaciones"])


@router.get("", response_model=list[NotificacionResponse])
def get_notificaciones(
    leida: bool | None = None,
    usuario_id: int | None = None,
    playa_id: int | None = None,
    db: Session = Depends(get_db),
) -> list[NotificacionResponse]:
    """List notifications with optional filters."""
    return list_notifications(db, leida=leida, usuario_id=usuario_id, playa_id=playa_id)


@router.put("/{notificacion_id}/leida", response_model=NotificacionLeidaResponse)
def mark_notificacion_as_read(
    notificacion_id: int,
    db: Session = Depends(get_db),
) -> NotificacionLeidaResponse:
    """Mark a notification as read."""
    notificacion = db.query(Notificacion).filter(Notificacion.id == notificacion_id).first()
    if notificacion is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notificación no encontrada",
        )
    notificacion.leida = True
    notificacion.deduplication_key = None
    db.commit()
    return NotificacionLeidaResponse(id=notificacion.id, leida=notificacion.leida)
