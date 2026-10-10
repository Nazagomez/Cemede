"""Machine learning routes."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.core.permissions import require_permission
from app.database import get_db
from app.models import Playa, Usuario
from app.schemas import MlEntrenarResponse, MlEstadoResponse, MlMetricasResponse, MlPrediccionResponse
from app.services import ml_service
from app.services.capacidad_service import construir_estimacion, obtener_eventos_activos, obtener_visitantes_activos
from app.models import ConfiguracionCcf

router = APIRouter(prefix="/ml", tags=["Machine Learning"])


def _get_playa(db: Session, playa_id: int) -> Playa:
    playa = db.query(Playa).filter(Playa.id == playa_id).first()
    if playa is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Playa no encontrada")
    return playa


@router.get("/estado/{playa_id}", response_model=MlEstadoResponse)
def get_estado_ml(
    playa_id: int,
    db: Session = Depends(get_db),
    _: Usuario = Depends(get_current_user),
) -> MlEstadoResponse:
    """Return ML model status for a beach."""
    _get_playa(db, playa_id)
    return MlEstadoResponse(**ml_service.get_ml_estado(db, playa_id))


@router.post("/entrenar/{playa_id}", response_model=MlEntrenarResponse)
def entrenar_modelo(
    playa_id: int,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_permission("ml.gestionar")),
) -> MlEntrenarResponse:
    """Train DecisionTreeRegressor for a beach."""
    _get_playa(db, playa_id)
    try:
        result = ml_service.train_model_for_playa(db, playa_id)
        db.commit()
    except ValueError as error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(error)) from error
    metricas = result["metricas"]
    return MlEntrenarResponse(
        playa_id=int(result["playa_id"]),
        modelo_activo=bool(result["modelo_activo"]),
        registros_usados=int(result["registros_usados"]),
        metricas=MlMetricasResponse(mae=float(metricas["mae"]), rmse=float(metricas["rmse"])),
        mensaje=str(result["mensaje"]),
    )


@router.get("/prediccion/{playa_id}", response_model=MlPrediccionResponse)
def get_prediccion_ml(
    playa_id: int,
    db: Session = Depends(get_db),
    _: Usuario = Depends(get_current_user),
) -> MlPrediccionResponse:
    """Return ML CCR prediction for current beach conditions."""
    playa = _get_playa(db, playa_id)
    config = db.query(ConfiguracionCcf).filter(ConfiguracionCcf.playa_id == playa_id).first()
    if config is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Configuración no encontrada")
    data = construir_estimacion(db, playa, config, guardar=False)
    estado = ml_service.get_ml_estado(db, playa_id)
    if not estado["modelo_activo"]:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No hay modelo ML activo para esta playa. Use CCR por fórmula.",
        )
    visitantes = obtener_visitantes_activos(db, playa_id)
    eventos = len(obtener_eventos_activos(db, playa_id))
    return MlPrediccionResponse(
        playa_id=playa_id,
        ccr_ml=float(data["ccr_ml"]) if data["ccr_ml"] is not None else None,
        ccr_formula=float(data["ccr_formula"]),
        variables_usadas={
            "visitantes_actuales": visitantes,
            "porcentaje_ocupacion": float(data["porcentaje_ocupacion"]),
            "eventos_activos": eventos,
        },
        modelo_activo=True,
        fecha_prediccion=data["fecha_calculo"],
    )
