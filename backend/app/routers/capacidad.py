"""Carrying capacity routes."""

from datetime import datetime
from typing import cast

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, get_optional_current_user
from app.core.permissions import require_permission
from app.database import get_db
from app.enums import MetodoCcr
from app.models import ConfiguracionCcf, EstimacionCapacidad, Playa, Usuario
from app.schemas import CapacidadCalcularResponse, CapacidadEstimacionResponse
from app.services.capacidad_service import (
    calcular_ccf,
    calcular_cce,
    calcular_ccr,
    construir_estimacion,
    obtener_factores_activos,
)
from app.services.notificacion_service import create_occupancy_notifications

router = APIRouter(prefix="/capacidad", tags=["Capacidad"])


def _get_playa(db: Session, playa_id: int) -> Playa:
    """Return beach by id or raise 404."""
    playa = db.query(Playa).filter(Playa.id == playa_id).first()
    if playa is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Playa no encontrada")
    return playa


def _get_playa_and_config(db: Session, playa_id: int) -> tuple[Playa, ConfiguracionCcf]:
    playa = _get_playa(db, playa_id)
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
        ccr_ml=float(cast(float, data["ccr_ml"])) if data.get("ccr_ml") is not None else None,
        ccr_final=float(cast(float, data["ccr_final"])),
        cce=float(cast(float, data["cce"])),
        metodo_ccr=MetodoCcr(str(data["metodo_ccr"])),
        visitantes_actuales=int(cast(int, data["visitantes_actuales"])),
        porcentaje_ocupacion=float(cast(float, data["porcentaje_ocupacion"])),
        eventos_activos=int(cast(int, data["eventos_activos"])),
        estado=str(data["estado"]),
    )


@router.get("/estimacion/{playa_id}", response_model=CapacidadEstimacionResponse)
def get_estimacion(
    playa_id: int,
    db: Session = Depends(get_db),
    _: Usuario | None = Depends(get_optional_current_user),
) -> CapacidadEstimacionResponse:
    """Get CCF, CCR and CCE estimation for a beach without persisting."""
    playa, config = _get_playa_and_config(db, playa_id)
    data = construir_estimacion(db, playa, config, guardar=False)
    return _build_estimacion_response(playa, data)


@router.get("/publico/{playa_id}", response_model=CapacidadEstimacionResponse)
def get_estimacion_publica(
    playa_id: int,
    db: Session = Depends(get_db),
) -> CapacidadEstimacionResponse:
    """Public CCF/CCR/CCE estimation for visitors — no auth required."""
    playa, config = _get_playa_and_config(db, playa_id)
    if not playa.activa:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Playa no encontrada")
    data = construir_estimacion(db, playa, config, guardar=False)
    return _build_estimacion_response(playa, data)


@router.post("/calcular/{playa_id}", response_model=CapacidadCalcularResponse, status_code=status.HTTP_201_CREATED)
def calcular_estimacion(
    playa_id: int,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_permission("capacidad.gestionar")),
) -> CapacidadCalcularResponse:
    """Recalculate capacity and persist the result in historial."""
    playa, config = _get_playa_and_config(db, playa_id)
    data = construir_estimacion(db, playa, config, guardar=True)
    estimacion_id = data.get("estimacion_id")
    if estimacion_id is None:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="No se pudo guardar la estimación")
    create_occupancy_notifications(
        db=db,
        playa_id=playa.id,
        playa_nombre=playa.nombre,
        estado=str(data["estado"]),
        porcentaje_ocupacion=float(cast(float, data["porcentaje_ocupacion"])),
    )
    db.commit()
    return CapacidadCalcularResponse(
        playa_id=playa.id,
        estimacion_id=int(cast(int, estimacion_id)),
        ccf=float(cast(float, data["ccf"])),
        ccr_final=float(cast(float, data["ccr_final"])),
        cce=float(cast(float, data["cce"])),
    )


@router.get("/ccf/{playa_id}")
def get_ccf(
    playa_id: int,
    db: Session = Depends(get_db),
    _: Usuario = Depends(get_current_user),
) -> dict[str, object]:
    """Calculate physical carrying capacity (CCF)."""
    playa, config = _get_playa_and_config(db, playa_id)
    ccf = calcular_ccf(
        float(playa.area_util_m2),
        float(config.area_por_visitante_m2),
        float(config.periodo_horas),
        float(config.tiempo_permanencia_horas),
    )
    return {
        "playa_id": playa.id,
        "playa_nombre": playa.nombre,
        "ccf": ccf,
        "fecha_calculo": datetime.utcnow(),
    }


@router.get("/ccr/{playa_id}")
def get_ccr(
    playa_id: int,
    db: Session = Depends(get_db),
    _: Usuario = Depends(get_current_user),
) -> dict[str, object]:
    """Calculate real carrying capacity (CCR)."""
    playa, config = _get_playa_and_config(db, playa_id)
    ccf = calcular_ccf(
        float(playa.area_util_m2),
        float(config.area_por_visitante_m2),
        float(config.periodo_horas),
        float(config.tiempo_permanencia_horas),
    )
    factores = obtener_factores_activos(db, playa_id)
    ccr_formula = calcular_ccr(ccf, factores if factores else [1.0])
    data = construir_estimacion(db, playa, config, guardar=False)
    return {
        "playa_id": playa.id,
        "ccf": ccf,
        "factores_correccion": factores if factores else [1.0],
        "ccr_formula": ccr_formula,
        "ccr_ml": data.get("ccr_ml"),
        "ccr_final": data["ccr_final"],
        "metodo_ccr": data["metodo_ccr"],
        "fecha_calculo": datetime.utcnow(),
    }


@router.get("/cce/{playa_id}")
def get_cce(
    playa_id: int,
    db: Session = Depends(get_db),
    _: Usuario = Depends(get_current_user),
) -> dict[str, object]:
    """Calculate effective carrying capacity (CCE)."""
    playa, config = _get_playa_and_config(db, playa_id)
    data = construir_estimacion(db, playa, config, guardar=False)
    return {
        "playa_id": playa.id,
        "ccr": data["ccr_final"],
        "capacidad_manejo": float(config.capacidad_manejo),
        "cce": data["cce"],
        "fecha_calculo": datetime.utcnow(),
    }


@router.get("/historial/{playa_id}")
def get_historial(
    playa_id: int,
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=10, ge=1, le=100),
    db: Session = Depends(get_db),
    _: Usuario = Depends(get_current_user),
) -> dict[str, object]:
    """Get historical capacity estimations, newest first."""
    _get_playa(db, playa_id)
    query = db.query(EstimacionCapacidad).filter(EstimacionCapacidad.playa_id == playa_id)
    total = query.count()
    estimaciones = (
        query.order_by(EstimacionCapacidad.fecha_calculo.desc())
        .offset((page - 1) * limit)
        .limit(limit)
        .all()
    )
    return {
        "playa_id": playa_id,
        "total": total,
        "page": page,
        "limit": limit,
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