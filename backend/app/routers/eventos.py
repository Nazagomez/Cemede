"""Environmental event routes."""

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.database import get_db
from app.enums import TipoEvento
from app.models import EventoAmbiental, FactorCorreccion, Playa, Usuario
from app.schemas import EventoAmbientalRequest, EventoAmbientalResponse
from app.services.capacidad_service import calcular_factor_correccion

router = APIRouter(prefix="/eventos", tags=["Eventos"])


@router.post("", response_model=EventoAmbientalResponse, status_code=status.HTTP_201_CREATED)
def crear_evento(
    payload: EventoAmbientalRequest,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
) -> EventoAmbientalResponse:
    """Report an environmental event."""
    playa = db.query(Playa).filter(Playa.id == payload.playa_id).first()
    if playa is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Playa no encontrada")
    factor = calcular_factor_correccion(payload.parte_afectada, payload.totalidad_analizada)
    evento = EventoAmbiental(
        playa_id=payload.playa_id,
        usuario_id=current_user.id,
        tipo=payload.tipo,
        titulo=payload.titulo,
        descripcion=payload.descripcion,
        fecha_inicio=payload.fecha_inicio,
        parte_afectada=payload.parte_afectada,
        totalidad_analizada=payload.totalidad_analizada,
        activo=True,
    )
    db.add(evento)
    db.flush()
    db.add(
        FactorCorreccion(
            evento_id=evento.id,
            nombre_variable=payload.tipo.value,
            valor=factor,
        )
    )
    db.commit()
    db.refresh(evento)
    return EventoAmbientalResponse(
        id=evento.id,
        playa_id=evento.playa_id,
        playa_nombre=playa.nombre,
        tipo=evento.tipo,
        titulo=evento.titulo,
        descripcion=evento.descripcion,
        fecha_inicio=evento.fecha_inicio,
        fecha_fin=evento.fecha_fin,
        factor_correccion=factor,
        activo=evento.activo,
        mensaje=f"Evento registrado. Factor de corrección = {factor}",
    )


def build_evento_response(evento: EventoAmbiental, playa_nombre: str | None) -> EventoAmbientalResponse:
    """Build environmental event API response."""
    factor = calcular_factor_correccion(float(evento.parte_afectada), float(evento.totalidad_analizada))
    return EventoAmbientalResponse(
        id=evento.id,
        playa_id=evento.playa_id,
        playa_nombre=playa_nombre,
        tipo=evento.tipo,
        titulo=evento.titulo,
        descripcion=evento.descripcion,
        fecha_inicio=evento.fecha_inicio,
        fecha_fin=evento.fecha_fin,
        factor_correccion=factor,
        activo=evento.activo,
    )


@router.get("", response_model=list[EventoAmbientalResponse])
def list_eventos(
    playa_id: int | None = None,
    tipo: TipoEvento | None = None,
    activo: bool | None = None,
    db: Session = Depends(get_db),
    _: Usuario = Depends(get_current_user),
) -> list[EventoAmbientalResponse]:
    """List environmental events with optional filters."""
    query = db.query(EventoAmbiental)
    if playa_id is not None:
        query = query.filter(EventoAmbiental.playa_id == playa_id)
    if tipo is not None:
        query = query.filter(EventoAmbiental.tipo == tipo)
    if activo is not None:
        query = query.filter(EventoAmbiental.activo.is_(activo))
    eventos = query.order_by(EventoAmbiental.fecha_inicio.desc()).all()
    playa_ids = {evento.playa_id for evento in eventos}
    playa_names: dict[int, str] = {}
    if playa_ids:
        playa_names = {
            playa.id: playa.nombre
            for playa in db.query(Playa).filter(Playa.id.in_(playa_ids)).all()
        }
    return [build_evento_response(evento, playa_names.get(evento.playa_id)) for evento in eventos]


@router.get("/activos/{playa_id}", response_model=list[EventoAmbientalResponse])
def list_eventos_activos(
    playa_id: int,
    db: Session = Depends(get_db),
    _: Usuario = Depends(get_current_user),
) -> list[EventoAmbientalResponse]:
    """List active environmental events for a beach."""
    playa = db.query(Playa).filter(Playa.id == playa_id).first()
    if playa is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Playa no encontrada")
    eventos = (
        db.query(EventoAmbiental)
        .filter(EventoAmbiental.playa_id == playa_id, EventoAmbiental.activo.is_(True))
        .all()
    )
    responses: list[EventoAmbientalResponse] = []
    for evento in eventos:
        factor = calcular_factor_correccion(float(evento.parte_afectada), float(evento.totalidad_analizada))
        responses.append(
            EventoAmbientalResponse(
                id=evento.id,
                playa_id=evento.playa_id,
                playa_nombre=playa.nombre,
                tipo=evento.tipo,
                titulo=evento.titulo,
                descripcion=evento.descripcion,
                fecha_inicio=evento.fecha_inicio,
                fecha_fin=evento.fecha_fin,
                factor_correccion=factor,
                activo=evento.activo,
            )
        )
    return responses


@router.put("/{evento_id}/cerrar", response_model=EventoAmbientalResponse)
def cerrar_evento(
    evento_id: int,
    db: Session = Depends(get_db),
    _: Usuario = Depends(get_current_user),
) -> EventoAmbientalResponse:
    """Close an active environmental event."""
    evento = db.query(EventoAmbiental).filter(EventoAmbiental.id == evento_id).first()
    if evento is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Evento no encontrado")
    playa = db.query(Playa).filter(Playa.id == evento.playa_id).first()
    evento.activo = False
    evento.fecha_fin = datetime.utcnow()
    db.commit()
    db.refresh(evento)
    factor = calcular_factor_correccion(float(evento.parte_afectada), float(evento.totalidad_analizada))
    return EventoAmbientalResponse(
        id=evento.id,
        playa_id=evento.playa_id,
        playa_nombre=playa.nombre if playa else None,
        tipo=evento.tipo,
        titulo=evento.titulo,
        descripcion=evento.descripcion,
        fecha_inicio=evento.fecha_inicio,
        fecha_fin=evento.fecha_fin,
        factor_correccion=factor,
        activo=evento.activo,
        mensaje="Evento cerrado correctamente",
    )
