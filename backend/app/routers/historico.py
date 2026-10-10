"""Historical visitation import routes."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.config import settings
from app.core.permissions import require_permission
from app.database import get_db
from app.models import Usuario, VisitacionHistorica
from app.schemas import HistoricoImportResponse, HistoricoSyncResponse, VisitacionHistoricaResponse
from app.services.historico_service import (
    generate_estimaciones_from_visitacion,
    import_visitacion_from_excel,
    sync_config_from_field_params,
)

router = APIRouter(prefix="/historico", tags=["Histórico"])


@router.post("/importar-excel", response_model=HistoricoImportResponse)
def importar_excel(
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_permission("ml.gestionar")),
) -> HistoricoImportResponse:
    """Import verified visitation workbook into visitacion_historica."""
    try:
        result = import_visitacion_from_excel(db, settings.visitacion_excel_path)
        db.commit()
    except (FileNotFoundError, ValueError) as error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(error)) from error
    return HistoricoImportResponse(
        inserted=result["inserted"],
        updated_or_skipped=result["updated_or_skipped"],
        mensaje="Importación de visitación histórica completada",
    )


@router.post("/sincronizar-estimaciones", response_model=HistoricoSyncResponse)
def sincronizar_estimaciones(
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_permission("capacidad.gestionar")),
) -> HistoricoSyncResponse:
    """Generate estimacion_capacidad rows from visitacion_historica."""
    configs = sync_config_from_field_params(db)
    result = generate_estimaciones_from_visitacion(db)
    db.commit()
    return HistoricoSyncResponse(
        configs_actualizadas=configs,
        estimaciones_creadas=result["created"],
        estimaciones_actualizadas=result["refreshed"],
        filas_fuente=result["total_source_rows"],
        mensaje="Estimaciones históricas sincronizadas",
    )


@router.get("/visitacion", response_model=list[VisitacionHistoricaResponse])
def list_visitacion_historica(
    playa_id: int | None = None,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_permission("capacidad.gestionar")),
) -> list[VisitacionHistoricaResponse]:
    """List imported historical visitation records."""
    query = db.query(VisitacionHistorica).order_by(VisitacionHistorica.anio.desc())
    if playa_id is not None:
        query = query.filter(VisitacionHistorica.playa_id == playa_id)
    return list(query.all())
