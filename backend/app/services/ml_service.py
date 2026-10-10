"""Machine learning services for CCR prediction (DecisionTreeRegressor)."""

from datetime import datetime
from pathlib import Path

import joblib
import numpy as np
from sklearn.metrics import mean_absolute_error, mean_squared_error
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeRegressor
from sqlalchemy.orm import Session

from app.config import settings
from app.enums import MetodoCcr
from app.models import EstimacionCapacidad, MlModelo

FEATURE_COLUMNS = ("visitantes_actuales", "porcentaje_ocupacion", "eventos_activos")


def _artifacts_dir() -> Path:
    """Return ML artifacts directory path."""
    base = Path(__file__).resolve().parents[2]
    target = Path(settings.ml_artifacts_dir)
    if not target.is_absolute():
        target = base / target
    target.mkdir(parents=True, exist_ok=True)
    return target


def _model_path(playa_id: int) -> Path:
    """Return filesystem path for a beach model artifact."""
    return _artifacts_dir() / f"playa_{playa_id}_decision_tree.joblib"


def count_estimaciones(db: Session, playa_id: int) -> int:
    """Count historical estimations available for training."""
    return db.query(EstimacionCapacidad).filter(EstimacionCapacidad.playa_id == playa_id).count()


def get_ml_estado(db: Session, playa_id: int) -> dict[str, object]:
    """Return ML model status for a beach."""
    total = count_estimaciones(db, playa_id)
    metadata = db.query(MlModelo).filter(MlModelo.playa_id == playa_id).first()
    modelo_activo = metadata is not None and metadata.activo and _model_path(playa_id).is_file()
    if total < settings.ml_registros_minimos:
        mensaje = "Datos insuficientes. Se utiliza CCR por fórmula."
    elif not modelo_activo:
        mensaje = "No hay modelo entrenado activo para esta playa."
    else:
        mensaje = "Modelo ML activo."
    return {
        "playa_id": playa_id,
        "modelo_activo": modelo_activo,
        "registros_disponibles": total,
        "registros_minimos": settings.ml_registros_minimos,
        "ultimo_entrenamiento": metadata.ultimo_entrenamiento if metadata else None,
        "mae": float(metadata.mae) if metadata and metadata.mae is not None else None,
        "rmse": float(metadata.rmse) if metadata and metadata.rmse is not None else None,
        "mensaje": mensaje,
    }


def _load_training_matrix(db: Session, playa_id: int) -> tuple[np.ndarray, np.ndarray]:
    """Build feature matrix X and target vector y from estimacion_capacidad."""
    rows = (
        db.query(EstimacionCapacidad)
        .filter(EstimacionCapacidad.playa_id == playa_id, EstimacionCapacidad.ccr_formula.isnot(None))
        .order_by(EstimacionCapacidad.fecha_calculo.asc())
        .all()
    )
    if not rows:
        raise ValueError("No hay estimaciones históricas para entrenar.")
    features: list[list[float]] = []
    targets: list[float] = []
    for row in rows:
        features.append(
            [
                float(row.visitantes_actuales),
                float(row.porcentaje_ocupacion),
                float(row.eventos_activos),
            ]
        )
        targets.append(float(row.ccr_formula))
    return np.array(features, dtype=float), np.array(targets, dtype=float)


def train_model_for_playa(db: Session, playa_id: int) -> dict[str, object]:
    """Train DecisionTreeRegressor and persist model metadata."""
    total = count_estimaciones(db, playa_id)
    if total < settings.ml_registros_minimos:
        raise ValueError(
            f"Datos insuficientes para entrenar. Se requieren al menos {settings.ml_registros_minimos} registros."
        )
    features, targets = _load_training_matrix(db, playa_id)
    train_x, test_x, train_y, test_y = train_test_split(
        features,
        targets,
        test_size=settings.ml_test_size,
        random_state=settings.ml_random_state,
    )
    model = DecisionTreeRegressor(
        max_depth=settings.ml_max_depth,
        min_samples_split=settings.ml_min_samples_split,
        min_samples_leaf=settings.ml_min_samples_leaf,
        random_state=settings.ml_random_state,
    )
    model.fit(train_x, train_y)
    predictions = model.predict(test_x)
    mae = float(mean_absolute_error(test_y, predictions))
    rmse = float(np.sqrt(mean_squared_error(test_y, predictions)))
    joblib.dump(model, _model_path(playa_id))
    metadata = db.query(MlModelo).filter(MlModelo.playa_id == playa_id).first()
    if metadata is None:
        metadata = MlModelo(playa_id=playa_id)
        db.add(metadata)
    metadata.activo = True
    metadata.registros_usados = total
    metadata.mae = mae
    metadata.rmse = rmse
    metadata.max_depth = settings.ml_max_depth
    metadata.min_samples_split = settings.ml_min_samples_split
    metadata.min_samples_leaf = settings.ml_min_samples_leaf
    metadata.random_state = settings.ml_random_state
    metadata.ultimo_entrenamiento = datetime.utcnow()
    db.flush()
    return {
        "playa_id": playa_id,
        "modelo_activo": True,
        "registros_usados": total,
        "metricas": {"mae": round(mae, 2), "rmse": round(rmse, 2)},
        "mensaje": "Modelo entrenado correctamente",
    }


def predict_ccr_ml(
    db: Session,
    playa_id: int,
    visitantes_actuales: int,
    porcentaje_ocupacion: float,
    eventos_activos: int,
) -> float | None:
    """Predict CCR using persisted model when active."""
    metadata = db.query(MlModelo).filter(MlModelo.playa_id == playa_id).first()
    model_path = _model_path(playa_id)
    if metadata is None or not metadata.activo or not model_path.is_file():
        return None
    if count_estimaciones(db, playa_id) < settings.ml_registros_minimos:
        return None
    model = joblib.load(model_path)
    sample = np.array([[visitantes_actuales, porcentaje_ocupacion, eventos_activos]], dtype=float)
    prediction = float(model.predict(sample)[0])
    return round(max(prediction, 0.0), 2)


def resolve_ccr_final(
    db: Session,
    playa_id: int,
    ccr_formula: float,
    visitantes_actuales: int,
    porcentaje_ocupacion: float,
    eventos_activos: int,
) -> tuple[float, float | None, MetodoCcr]:
    """Choose final CCR using ML when model is active, otherwise formula."""
    ccr_ml = predict_ccr_ml(
        db=db,
        playa_id=playa_id,
        visitantes_actuales=visitantes_actuales,
        porcentaje_ocupacion=porcentaje_ocupacion,
        eventos_activos=eventos_activos,
    )
    if ccr_ml is None:
        return ccr_formula, None, MetodoCcr.FORMULA
    return ccr_ml, ccr_ml, MetodoCcr.MACHINE_LEARNING
