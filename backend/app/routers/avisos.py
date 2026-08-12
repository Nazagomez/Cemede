"""Public announcement routes."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import AvisoPublicoResponse
from app.services.aviso_service import list_public_avisos

router = APIRouter(prefix="/avisos", tags=["Avisos"])


@router.get("/publicos", response_model=list[AvisoPublicoResponse])
def get_avisos_publicos(
    playa_id: int | None = None,
    limit: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
) -> list[AvisoPublicoResponse]:
    """List public announcements for the main page."""
    return list_public_avisos(db, playa_id=playa_id, limit=limit)
