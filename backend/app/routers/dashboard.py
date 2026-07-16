"""Dashboard routes."""

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.database import get_db
from app.models import ConfiguracionCcf, EstimacionCapacidad, EventoAmbiental, Playa, Usuario
from app.schemas import DashboardPlayaResponse, PlayaResponse
from app.services.capacidad_service import calcular_factor_correccion, construir_estimacion

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/{playa_id}", response_model=DashboardPlayaResponse)
def get_dashboard_playa(
    playa_id: int,
    db: Session = Depends(get_db),
    _: Usuario = Depends(get_current_user),
) -> DashboardPlayaResponse:
    """Get dashboard summary for one beach."""
    playa = db.query(Playa).filter(Playa.id == playa_id).first()
    if playa is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Playa no encontrada")
    config = db.query(ConfiguracionCcf).filter(ConfiguracionCcf.playa_id == playa_id).first()
    if config is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Configuración no encontrada")
    data = construir_estimacion(db, playa, config)
    eventos = (
        db.query(EventoAmbiental)
        .filter(EventoAmbiental.playa_id == playa_id, EventoAmbiental.activo.is_(True))
        .all()
    )
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
        eventos_activos=[
            {
                "id": evento.id,
                "tipo": evento.tipo.value,
                "titulo": evento.titulo,
                "factor_correccion": calcular_factor_correccion(
                    float(evento.parte_afectada),
                    float(evento.totalidad_analizada),
                ),
            }
            for evento in eventos
        ],
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
        eventos_count = (
            db.query(EventoAmbiental)
            .filter(EventoAmbiental.playa_id == playa.id, EventoAmbiental.activo.is_(True))
            .count()
        )
        items.append(
            {
                "id": playa.id,
                "nombre": playa.nombre,
                "visitantes_actuales": int(data["visitantes_actuales"]),
                "porcentaje_ocupacion": float(data["porcentaje_ocupacion"]),
                "estado": str(data["estado"]),
                "eventos_activos": eventos_count,
            }
        )
    return {
        "fecha_consulta": datetime.utcnow().isoformat(),
        "total_playas": len(items),
        "playas": items,
    }
