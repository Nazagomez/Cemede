"""Carrying capacity routes."""

from datetime import datetime
from typing import cast

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.database import get_db
from app.enums import MetodoCcr
from app.models import ConfiguracionCcf, EstimacionCapacidad, Playa, Usuario
from app.schemas import CapacidadCalcularResponse, CapacidadEstimacionResponse
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


def _build_estimacion_response(playa: Playa, data: dict[str, object]) -> CapacidadEstimacionResponse:
    """Build capacity estimation API response from service data."""
    return CapacidadEstimacionResponse(
        playa_id=playa.id,
        playa_nombre=playa.nombre,
        fecha_calculo=cast(datetime, data["fecha_calculo"]),
        ccf=float(cast(float, data["ccf"])),
        ccr_formula=float(cast(float, data["ccr_formula"])),
        ccr_ml=None,
        ccr_final=float(cast(float, data["ccr_final"])),
        cce=float(cast(float, data["cce"])),
        metodo_ccr=MetodoCcr.FORMULA,
        visitantes_actuales=int(cast(int, data["visitantes_actuales"])),
        porcentaje_ocupacion=float(cast(float, data["porcentaje_ocupacion"])),
        eventos_activos=int(cast(int, data["eventos_activos"])),
        estado=str(data["estado"]),
    )


@router.get("/estimacion/{playa_id}", response_model=CapacidadEstimacionResponse)
def get_estimacion(
    playa_id: int,
    db: Session = Depends(get_db),
    _: Usuario = Depends(get_current_user),
) -> CapacidadEstimacionResponse:
    """Get CCF, CCR and CCE estimation for a beach without persisting."""
    playa, config = _get_playa_and_config(db, playa_id)
    data = construir_estimacion(db, playa, config, guardar=False)
    return _build_estimacion_response(playa, data)


@router.post("/calcular/{playa_id}", response_model=CapacidadCalcularResponse, status_code=status.HTTP_201_CREATED)
def calcular_estimacion(
    playa_id: int,
    db: Session = Depends(get_db),
    _: Usuario = Depends(get_current_user),
) -> CapacidadCalcularResponse:
    """Recalculate capacity and persist the result in historial."""
    playa, config = _get_playa_and_config(db, playa_id)
    data = construir_estimacion(db, playa, config, guardar=True)
    estimacion_id = data.get("estimacion_id")
    if estimacion_id is None:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="No se pudo guardar la estimación")
    return CapacidadCalcularResponse(
        playa_id=playa.id,
        estimacion_id=int(cast(int, estimacion_id)),
        ccf=float(cast(float, data["ccf"])),
        ccr_final=float(cast(float, data["ccr_final"])),
        cce=float(cast(float, data["cce"])),
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
