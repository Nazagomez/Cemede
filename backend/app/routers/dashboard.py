"""Dashboard routes."""

from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.database import get_db
from app.models import ConfiguracionCcf, EstimacionCapacidad, Playa, Usuario
from app.routers.playas import get_active_playa
from app.schemas import DashboardPlayaResponse, PlayaResponse
from app.services.capacidad_service import build_eventos_activos_resumen, construir_estimacion

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/tendencia")
def get_dashboard_tendencia(
    dias: int = Query(default=7, ge=1, le=90),
    db: Session = Depends(get_db),
    _: Usuario = Depends(get_current_user),
) -> dict[str, object]:
    """Get occupancy trend across active beaches for the last N days.

    One point per calendar day per beach: the last estimation recorded
    that day (estimations are ordered ascending, so later rows overwrite
    earlier ones for the same date).
    """
    desde = datetime.utcnow() - timedelta(days=dias)
    playas = db.query(Playa).filter(Playa.activa.is_(True)).all()
    playa_nombres = {playa.id: playa.nombre for playa in playas}

    if not playa_nombres:
        return {"dias": dias, "playas": [], "datos": []}

    estimaciones = (
        db.query(EstimacionCapacidad)
        .filter(
            EstimacionCapacidad.playa_id.in_(playa_nombres.keys()),
            EstimacionCapacidad.fecha_calculo >= desde,
        )
        .order_by(EstimacionCapacidad.fecha_calculo.asc())
        .all()
    )

    datos_por_fecha: dict[str, dict[str, float | str]] = {}
    for estimacion in estimaciones:
        clave = estimacion.fecha_calculo.date().isoformat()
        fila = datos_por_fecha.setdefault(clave, {"fecha": clave})
        nombre = playa_nombres.get(estimacion.playa_id)
        if nombre is not None:
            fila[nombre] = float(estimacion.porcentaje_ocupacion)

    datos = [datos_por_fecha[clave] for clave in sorted(datos_por_fecha.keys())]

    return {
        "dias": dias,
        "playas": list(playa_nombres.values()),
        "datos": datos,
    }


@router.get("/{playa_id}", response_model=DashboardPlayaResponse)
def get_dashboard_playa(
    playa_id: int,
    db: Session = Depends(get_db),
    _: Usuario = Depends(get_current_user),
) -> DashboardPlayaResponse:
    """Get dashboard summary for one beach."""
    playa = get_active_playa(db, playa_id)
    config = db.query(ConfiguracionCcf).filter(ConfiguracionCcf.playa_id == playa_id).first()
    if config is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Configuración no encontrada")
    data = construir_estimacion(db, playa, config)
    ultimas = (
        db.query(EstimacionCapacidad)
        .filter(EstimacionCapacidad.playa_id == playa_id)
        .order_by(EstimacionCapacidad.fecha_calculo.desc())
        .limit(5)
        .all()
    )
    return DashboardPlayaResponse(
        playa=PlayaResponse.model_validate(playa),
        ocupacion={
            "visitantes_actuales": int(data["visitantes_actuales"]),
            "porcentaje": float(data["porcentaje_ocupacion"]),
            "estado": str(data["estado"]),
        },
        capacidad={
            "ccf": float(data["ccf"]),
            "ccr": float(data["ccr_final"]),
            "cce": float(data["cce"]),
            "metodo_ccr": str(data["metodo_ccr"]),
        },
        eventos_activos=build_eventos_activos_resumen(db, playa_id),
        ultimas_estimaciones=[
            {
                "fecha": item.fecha_calculo.isoformat(),
                "porcentaje_ocupacion": float(item.porcentaje_ocupacion),
            }
            for item in ultimas
        ],
    )


@router.get("")
def get_dashboard_general(
    db: Session = Depends(get_db),
    _: Usuario = Depends(get_current_user),
) -> dict[str, object]:
    """Get dashboard summary for all beaches."""
    playas = db.query(Playa).filter(Playa.activa.is_(True)).all()
    items: list[dict[str, object]] = []
    for playa in playas:
        config = db.query(ConfiguracionCcf).filter(ConfiguracionCcf.playa_id == playa.id).first()
        if config is None:
            continue
        data = construir_estimacion(db, playa, config)
        items.append(
            {
                "id": playa.id,
                "nombre": playa.nombre,
                "visitantes_actuales": int(data["visitantes_actuales"]),
                "porcentaje_ocupacion": float(data["porcentaje_ocupacion"]),
                "estado": str(data["estado"]),
                "eventos_activos": int(data["eventos_activos"]),
            }
        )
    return {
        "fecha_consulta": datetime.utcnow().isoformat(),
        "total_playas": len(items),
        "playas": items,
    }