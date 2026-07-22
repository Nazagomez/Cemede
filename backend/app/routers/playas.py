"""Beach routes."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, require_admin
from app.database import get_db
from app.models import ConfiguracionCcf, Playa, Usuario
from app.schemas import ConfiguracionCcfResponse, ConfiguracionCcfUpdate, MessageResponse, PlayaResponse

router = APIRouter(prefix="/playas", tags=["Playas"])


@router.get("", response_model=list[PlayaResponse])
def list_playas(db: Session = Depends(get_db), _: Usuario = Depends(get_current_user)) -> list[Playa]:
    """List all beaches."""
    return db.query(Playa).filter(Playa.activa.is_(True)).all()


@router.get("/{playa_id}", response_model=PlayaResponse)
def get_playa(playa_id: int, db: Session = Depends(get_db), _: Usuario = Depends(get_current_user)) -> Playa:
    """Get beach by id."""
    playa = db.query(Playa).filter(Playa.id == playa_id).first()
    if playa is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Playa no encontrada")
    return playa


@router.get("/{playa_id}/configuracion", response_model=ConfiguracionCcfResponse)
def get_configuracion(
    playa_id: int,
    db: Session = Depends(get_db),
    _: Usuario = Depends(get_current_user),
) -> ConfiguracionCcfResponse:
    """Get CCF configuration for a beach."""
    config = db.query(ConfiguracionCcf).filter(ConfiguracionCcf.playa_id == playa_id).first()
    if config is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Configuración no encontrada")
    return ConfiguracionCcfResponse(
        playa_id=config.playa_id,
        area_por_visitante_m2=float(config.area_por_visitante_m2),
        periodo_horas=config.periodo_horas,
        tiempo_permanencia_horas=float(config.tiempo_permanencia_horas),
        capacidad_manejo=float(config.capidad_manejo),
        updated_at=config.updated_at,
    )


@router.put("/{playa_id}/configuracion", response_model=ConfiguracionCcfResponse)
def update_configuracion(
    playa_id: int,
    payload: ConfiguracionCcfUpdate,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_admin),
) -> ConfiguracionCcfResponse:
    """Update CCF configuration (admin only)."""
    config = db.query(ConfiguracionCcf).filter(ConfiguracionCcf.playa_id == playa_id).first()
    if config is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Configuración no encontrada")
    config.area_por_visitante_m2 = payload.area_por_visitante_m2
    config.periodo_horas = payload.periodo_horas
    config.tiempo_permanencia_horas = payload.tiempo_permanencia_horas
    config.capacidad_manejo = payload.capacidad_manejo
    db.commit()
    db.refresh(config)
    return ConfiguracionCcfResponse(
        playa_id=config.playa_id,
        area_por_visitante_m2=float(config.area_por_visitante_m2),
        periodo_horas=config.periodo_horas,
        tiempo_permanencia_horas=float(config.tiempo_permanencia_horas),
        capacidad_manejo=float(config.capacidad_manejo),
        updated_at=config.updated_at,
    )
