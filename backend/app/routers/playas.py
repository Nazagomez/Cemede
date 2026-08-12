"""Beach routes."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, require_admin
from app.database import get_db
from app.models import ConfiguracionCcf, Playa, Usuario
from app.schemas import ConfiguracionCcfResponse, ConfiguracionCcfUpdate, PlayaCreate, PlayaResponse
from app.services.capacidad_service import obtener_visitantes_activos

router = APIRouter(prefix="/playas", tags=["Playas"])

CONFIGURACION_ACTUALIZADA_MENSAJE = "Configuración actualizada correctamente"
PLAYA_CREADA_MENSAJE = "Playa registrada correctamente"
PLAYA_BAJA_MENSAJE = "Playa dada de baja correctamente"


def get_playa_by_id(db: Session, playa_id: int) -> Playa:
    """Return a beach by id or raise 404."""
    playa = db.query(Playa).filter(Playa.id == playa_id).first()
    if playa is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Playa no encontrada")
    return playa


def build_playa_response(playa: Playa, mensaje: str | None = None) -> PlayaResponse:
    """Build beach API response."""
    return PlayaResponse.model_validate(playa).model_copy(update={"mensaje": mensaje})


def get_active_playa(db: Session, playa_id: int) -> Playa:
    """Return an active beach or raise 404."""
    playa = db.query(Playa).filter(Playa.id == playa_id, Playa.activa.is_(True)).first()
    if playa is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Playa no encontrada")
    return playa


def build_configuracion_response(
    config: ConfiguracionCcf,
    mensaje: str | None = None,
) -> ConfiguracionCcfResponse:
    """Build CCF configuration API response."""
    return ConfiguracionCcfResponse(
        playa_id=config.playa_id,
        area_por_visitante_m2=float(config.area_por_visitante_m2),
        periodo_horas=config.periodo_horas,
        tiempo_permanencia_horas=float(config.tiempo_permanencia_horas),
        capacidad_manejo=float(config.capacidad_manejo),
        updated_at=config.updated_at,
        mensaje=mensaje,
    )


@router.get("", response_model=list[PlayaResponse])
def list_playas(db: Session = Depends(get_db), _: Usuario = Depends(get_current_user)) -> list[Playa]:
    """List all active beaches."""
    return db.query(Playa).filter(Playa.activa.is_(True)).all()


@router.post("", response_model=PlayaResponse, status_code=status.HTTP_201_CREATED)
def create_playa(
    payload: PlayaCreate,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_admin),
) -> PlayaResponse:
    """Register a new beach with default CCF configuration (admin only)."""
    playa = Playa(
        nombre=payload.nombre,
        descripcion=payload.descripcion,
        area_util_m2=payload.area_util_m2,
        canton=payload.canton,
        provincia=payload.provincia,
        latitud=payload.latitud,
        longitud=payload.longitud,
        activa=True,
    )
    db.add(playa)
    db.flush()
    db.add(
        ConfiguracionCcf(
            playa_id=playa.id,
            area_por_visitante_m2=payload.area_por_visitante_m2,
            periodo_horas=payload.periodo_horas,
            tiempo_permanencia_horas=payload.tiempo_permanencia_horas,
            capacidad_manejo=payload.capacidad_manejo,
        )
    )
    db.commit()
    db.refresh(playa)
    return build_playa_response(playa, mensaje=PLAYA_CREADA_MENSAJE)


@router.get("/{playa_id}", response_model=PlayaResponse)
def get_playa(
    playa_id: int,
    db: Session = Depends(get_db),
    _: Usuario = Depends(get_current_user),
) -> Playa:
    """Get beach by id."""
    return get_active_playa(db, playa_id)


@router.get("/{playa_id}/configuracion", response_model=ConfiguracionCcfResponse)
def get_configuracion(
    playa_id: int,
    db: Session = Depends(get_db),
    _: Usuario = Depends(get_current_user),
) -> ConfiguracionCcfResponse:
    """Get CCF configuration for a beach."""
    get_active_playa(db, playa_id)
    config = db.query(ConfiguracionCcf).filter(ConfiguracionCcf.playa_id == playa_id).first()
    if config is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Configuración no encontrada")
    return build_configuracion_response(config)


@router.put("/{playa_id}/configuracion", response_model=ConfiguracionCcfResponse)
def update_configuracion(
    playa_id: int,
    payload: ConfiguracionCcfUpdate,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_admin),
) -> ConfiguracionCcfResponse:
    """Update CCF configuration (admin only)."""
    get_active_playa(db, playa_id)
    config = db.query(ConfiguracionCcf).filter(ConfiguracionCcf.playa_id == playa_id).first()
    if config is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Configuración no encontrada")
    config.area_por_visitante_m2 = payload.area_por_visitante_m2
    config.periodo_horas = payload.periodo_horas
    config.tiempo_permanencia_horas = payload.tiempo_permanencia_horas
    config.capacidad_manejo = payload.capacidad_manejo
    db.commit()
    db.refresh(config)
    return build_configuracion_response(config, mensaje=CONFIGURACION_ACTUALIZADA_MENSAJE)


@router.delete("/{playa_id}", response_model=PlayaResponse)
def deactivate_playa(
    playa_id: int,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_admin),
) -> PlayaResponse:
    """Soft-delete a beach by marking it inactive (admin only)."""
    playa = get_playa_by_id(db, playa_id)
    if not playa.activa:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Playa ya está dada de baja")
    if obtener_visitantes_activos(db, playa_id) > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No se puede dar de baja una playa con visitantes activos",
        )
    playa.activa = False
    db.commit()
    db.refresh(playa)
    return build_playa_response(playa, mensaje=PLAYA_BAJA_MENSAJE)
