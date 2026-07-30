"""Authenticated user notification routes."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.database import get_db
from app.models import Notificacion, Usuario
from app.schemas import NotificacionLeidaResponse, NotificacionResponse
from app.services.notificacion_service import list_user_notifications

router = APIRouter(prefix="/notificaciones", tags=["Notificaciones"])


@router.get("", response_model=list[NotificacionResponse])
def get_notificaciones(
    leida: bool | None = None,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
) -> list[NotificacionResponse]:
    """List notifications belonging to the authenticated user."""
    return list_user_notifications(db, current_user.id, leida)


@router.put("/{notificacion_id}/leida", response_model=NotificacionLeidaResponse)
def mark_notificacion_as_read(
    notificacion_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
) -> NotificacionLeidaResponse:
    """Mark one of the authenticated user's notifications as read."""
    notificacion = (
        db.query(Notificacion)
        .filter(
            Notificacion.id == notificacion_id,
            Notificacion.usuario_id == current_user.id,
        )
        .first()
    )
    if notificacion is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notificación no encontrada",
        )
    notificacion.leida = True
    db.commit()
    return NotificacionLeidaResponse(id=notificacion.id, leida=notificacion.leida)
