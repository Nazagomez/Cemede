"""Environmental event routes."""

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, get_optional_current_user
from app.database import get_db
from app.enums import EstadoEvento, OrigenEvento, TipoEvento
from app.models import EventoAmbiental, FactorCorreccion, Playa, Usuario
from app.schemas import EventoAmbientalRequest, EventoAmbientalResponse
from app.services.capacidad_service import (
    calcular_factor_correccion,
    get_stored_factors_by_evento,
    resolve_factor_correccion,
)
from app.services.evento_service import (
    ensure_evento_is_approved,
    ensure_evento_is_pending,
    notify_evento_aprobado,
    notify_evento_cerrado,
    notify_evento_pendiente,
    notify_evento_rechazado,
    resolve_evento_origen,
)

router = APIRouter(prefix="/eventos", tags=["Eventos"])


def build_evento_response(
    evento: EventoAmbiental,
    playa_nombre: str | None,
    factor_correccion: float | None,
    mensaje: str | None = None,
) -> EventoAmbientalResponse:
    """Build environmental event API response."""
    return EventoAmbientalResponse(
        id=evento.id,
        playa_id=evento.playa_id,
        playa_nombre=playa_nombre,
        tipo=evento.tipo,
        titulo=evento.titulo,
        descripcion=evento.descripcion,
        fecha_inicio=evento.fecha_inicio,
        fecha_fin=evento.fecha_fin,
        factor_correccion=factor_correccion,
        activo=evento.activo,
        estado=evento.estado,
        origen=evento.origen,
        reportado_por=evento.reportado_por,
        mensaje=mensaje,
    )


def build_evento_responses(
    db: Session,
    eventos: list[EventoAmbiental],
    playa_names: dict[int, str],
) -> list[EventoAmbientalResponse]:
    """Build event responses using persisted correction factors when available."""
    stored_factors = get_stored_factors_by_evento(db, [evento.id for evento in eventos])
    return [
        build_evento_response(
            evento=evento,
            playa_nombre=playa_names.get(evento.playa_id),
            factor_correccion=(
                resolve_factor_correccion(evento, stored_factors)
                if evento.id in stored_factors
                else None
            ),
        )
        for evento in eventos
    ]


def _get_evento_or_404(db: Session, evento_id: int) -> EventoAmbiental:
    evento = db.query(EventoAmbiental).filter(EventoAmbiental.id == evento_id).first()
    if evento is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Evento no encontrado")
    return evento


@router.post("", response_model=EventoAmbientalResponse, status_code=status.HTTP_201_CREATED)
def crear_evento(
    payload: EventoAmbientalRequest,
    db: Session = Depends(get_db),
    current_user: Usuario | None = Depends(get_optional_current_user),
) -> EventoAmbientalResponse:
    """Report an environmental event pending administrator approval."""
    playa = db.query(Playa).filter(Playa.id == payload.playa_id, Playa.activa.is_(True)).first()
    if playa is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Playa no encontrada")
    origen = resolve_evento_origen(current_user)
    evento = EventoAmbiental(
        playa_id=payload.playa_id,
        usuario_id=current_user.id if current_user is not None else None,
        tipo=payload.tipo,
        titulo=payload.titulo,
        descripcion=payload.descripcion,
        fecha_inicio=payload.fecha_inicio,
        parte_afectada=payload.parte_afectada,
        totalidad_analizada=payload.totalidad_analizada,
        activo=False,
        estado=EstadoEvento.PENDIENTE,
        origen=origen,
        reportado_por=payload.reportado_por,
    )
    db.add(evento)
    db.flush()
    notify_evento_pendiente(db, evento, playa.nombre)
    db.commit()
    db.refresh(evento)
    return build_evento_response(
        evento=evento,
        playa_nombre=playa.nombre,
        factor_correccion=None,
        mensaje="Evento registrado y enviado para aprobación del administrador",
    )


@router.get("/pendientes", response_model=list[EventoAmbientalResponse])
def list_eventos_pendientes(
    db: Session = Depends(get_db),
    _: Usuario = Depends(get_current_user),
) -> list[EventoAmbientalResponse]:
    """List environmental events waiting for approval (admin or asistente)."""
    eventos = (
        db.query(EventoAmbiental)
        .filter(EventoAmbiental.estado == EstadoEvento.PENDIENTE)
        .order_by(EventoAmbiental.created_at.desc())
        .all()
    )
    playa_ids = {evento.playa_id for evento in eventos}
    playa_names = {
        playa.id: playa.nombre
        for playa in db.query(Playa).filter(Playa.id.in_(playa_ids)).all()
    } if playa_ids else {}
    return build_evento_responses(db, eventos, playa_names)


@router.get("", response_model=list[EventoAmbientalResponse])
def list_eventos(
    playa_id: int | None = None,
    tipo: TipoEvento | None = None,
    activo: bool | None = None,
    estado: EstadoEvento | None = None,
    db: Session = Depends(get_db),
) -> list[EventoAmbientalResponse]:
    """List environmental events with optional filters."""
    query = db.query(EventoAmbiental)
    if playa_id is not None:
        query = query.filter(EventoAmbiental.playa_id == playa_id)
    if tipo is not None:
        query = query.filter(EventoAmbiental.tipo == tipo)
    if activo is not None:
        query = query.filter(EventoAmbiental.activo.is_(activo))
    if estado is not None:
        query = query.filter(EventoAmbiental.estado == estado)
    eventos = query.order_by(EventoAmbiental.fecha_inicio.desc()).all()
    playa_ids = {evento.playa_id for evento in eventos}
    playa_names = {
        playa.id: playa.nombre
        for playa in db.query(Playa).filter(Playa.id.in_(playa_ids)).all()
    } if playa_ids else {}
    return build_evento_responses(db, eventos, playa_names)


@router.get("/activos/{playa_id}", response_model=list[EventoAmbientalResponse])
def list_eventos_activos(
    playa_id: int,
    db: Session = Depends(get_db),
) -> list[EventoAmbientalResponse]:
    """List approved and active environmental events for a beach."""
    playa = db.query(Playa).filter(Playa.id == playa_id).first()
    if playa is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Playa no encontrada")
    eventos = (
        db.query(EventoAmbiental)
        .filter(
            EventoAmbiental.playa_id == playa_id,
            EventoAmbiental.estado == EstadoEvento.APROBADO,
            EventoAmbiental.activo.is_(True),
        )
        .all()
    )
    return build_evento_responses(db, eventos, {playa.id: playa.nombre})


@router.put("/{evento_id}/aprobar", response_model=EventoAmbientalResponse)
def aprobar_evento(
    evento_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
) -> EventoAmbientalResponse:
    """Approve a pending environmental event and activate its correction factor (admin or asistente)."""
    evento = _get_evento_or_404(db, evento_id)
    ensure_evento_is_pending(evento)
    playa = db.query(Playa).filter(Playa.id == evento.playa_id).first()
    if playa is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Playa no encontrada")
    factor = calcular_factor_correccion(float(evento.parte_afectada), float(evento.totalidad_analizada))
    evento.estado = EstadoEvento.APROBADO
    evento.activo = True
    evento.aprobado_por = current_user.id
    evento.fecha_aprobacion = datetime.utcnow()
    db.add(
        FactorCorreccion(
            evento_id=evento.id,
            nombre_variable=evento.tipo.value,
            valor=factor,
        )
    )
    notify_evento_aprobado(db, evento, playa.nombre, factor)
    db.commit()
    db.refresh(evento)
    return build_evento_response(
        evento=evento,
        playa_nombre=playa.nombre,
        factor_correccion=factor,
        mensaje=f"Evento aprobado. Factor de corrección = {factor}",
    )


@router.put("/{evento_id}/rechazar", response_model=EventoAmbientalResponse)
def rechazar_evento(
    evento_id: int,
    db: Session = Depends(get_db),
    _: Usuario = Depends(get_current_user),
) -> EventoAmbientalResponse:
    """Reject a pending environmental event (admin or asistente)."""
    evento = _get_evento_or_404(db, evento_id)
    ensure_evento_is_pending(evento)
    playa = db.query(Playa).filter(Playa.id == evento.playa_id).first()
    evento.estado = EstadoEvento.RECHAZADO
    evento.activo = False
    if playa is not None:
        notify_evento_rechazado(db, evento)
    db.commit()
    db.refresh(evento)
    return build_evento_response(
        evento=evento,
        playa_nombre=playa.nombre if playa else None,
        factor_correccion=None,
        mensaje="Evento rechazado correctamente",
    )


@router.put("/{evento_id}/cerrar", response_model=EventoAmbientalResponse)
def cerrar_evento(
    evento_id: int,
    db: Session = Depends(get_db),
    _: Usuario = Depends(get_current_user),
) -> EventoAmbientalResponse:
    """Close an approved and active environmental event."""
    evento = _get_evento_or_404(db, evento_id)
    ensure_evento_is_approved(evento)
    playa = db.query(Playa).filter(Playa.id == evento.playa_id).first()
    stored_factors = get_stored_factors_by_evento(db, [evento.id])
    factor = resolve_factor_correccion(evento, stored_factors) if stored_factors else None
    evento.estado = EstadoEvento.CERRADO
    evento.activo = False
    evento.fecha_fin = datetime.utcnow()
    if playa is not None:
        notify_evento_cerrado(db, evento, playa.nombre)
    db.commit()
    db.refresh(evento)
    return build_evento_response(
        evento=evento,
        playa_nombre=playa.nombre if playa else None,
        factor_correccion=factor,
        mensaje="Evento cerrado correctamente",
    )