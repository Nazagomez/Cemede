"""Carrying capacity routes."""

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.database import get_db
from app.enums import MetodoCcr
from app.models import ConfiguracionCcf, EstimacionCapacidad, Playa, Usuario
from app.schemas import CapacidadEstimacionResponse
from app.services.capacidad_service import construir_estimacion

router = APIRouter(prefix="/capacidad", tags=["Capacidad"])


def _get_playa_and_config(db: Session, playa_id: int) -> tuple[Playa, ConfiguracionCcf]:
    playa = db.query(Playa).filter(Playa.id == playa_id).first()
    if playa is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Playa no encontrada")
    config = db.query(ConfiguracionCcf).filter(ConfiguracionCcf.playa_id == playa_id).first()
    if config is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Configuración no encontrada")
    return playa, config


@router.get("/estimacion/{playa_id}", response_model=CapacidadEstimacionResponse)
def get_estimacion(
    playa_id: int,
    db: Session = Depends(get_db),
    _: Usuario = Depends(get_current_user),
) -> CapacidadEstimacionResponse:
    """Get CCF, CCR and CCE estimation for a beach."""
    playa, config = _get_playa_and_config(db, playa_id)
    data = construir_estimacion(db, playa, config, guardar=True)
    return CapacidadEstimacionResponse(
        playa_id=playa.id,
        playa_nombre=playa.nombre,
        fecha_calculo=datetime.utcnow(),
        ccf=float(data["ccf"]),
        ccr_formula=float(data["ccr_formula"]),
        ccr_ml=None,
        ccr_final=float(data["ccr_final"]),
        cce=float(data["cce"]),
        metodo_ccr=MetodoCcr.FORMULA,
        visitantes_actuales=int(data["visitantes_actuales"]),
        porcentaje_ocupacion=float(data["porcentaje_ocupacion"]),
        eventos_activos=int(data["eventos_activos"]),
        estado=str(data["estado"]),
    )


@router.get("/historial/{playa_id}")
def get_historial(
    playa_id: int,
    limit: int = 30,
    db: Session = Depends(get_db),
    _: Usuario = Depends(get_current_user),
) -> dict[str, object]:
    """Get historical capacity estimations."""
    estimaciones = (
        db.query(EstimacionCapacidad)
        .filter(EstimacionCapacidad.playa_id == playa_id)
        .order_by(EstimacionCapacidad.fecha_calculo.desc())
        .limit(limit)
        .all()
    )
    return {
        "playa_id": playa_id,
        "total": len(estimaciones),
        "estimaciones": [
            {
                "id": item.id,
                "fecha_calculo": item.fecha_calculo,
                "ccf": float(item.ccf),
                "ccr_final": float(item.ccr_final),
                "cce": float(item.cce),
                "visitantes_actuales": item.visitantes_actuales,
                "porcentaje_ocupacion": float(item.porcentaje_ocupacion),
            }
            for item in estimaciones
        ],
    }
