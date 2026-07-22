"""Visitor registration routes."""

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.database import get_db
from app.models import Playa, RegistroVisitante, Usuario
from app.schemas import EntradaVisitanteRequest, OcupacionResponse, RegistroVisitanteResponse, SalidaVisitanteRequest
from app.services.capacidad_service import obtener_visitantes_activos

router = APIRouter(prefix="/visitantes", tags=["Visitantes"])


@router.post("/entrada", response_model=RegistroVisitanteResponse, status_code=status.HTTP_201_CREATED)
def registrar_entrada(
    payload: EntradaVisitanteRequest,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
) -> RegistroVisitanteResponse:
    """Register visitor entry."""
    playa = db.query(Playa).filter(Playa.id == payload.playa_id, Playa.activa.is_(True)).first()
    if playa is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Playa no encontrada")
    registro = RegistroVisitante(
        playa_id=payload.playa_id,
        usuario_id=current_user.id,
        fecha_entrada=datetime.utcnow(),
        cantidad_personas=payload.cantidad_personas,
        observaciones=payload.observaciones,
    )
    db.add(registro)
    db.commit()
    db.refresh(registro)
    return RegistroVisitanteResponse(
        id=registro.id,
        playa_id=registro.playa_id,
        playa_nombre=playa.nombre,
        usuario_id=registro.usuario_id,
        fecha_entrada=registro.fecha_entrada,
        fecha_salida=registro.fecha_salida,
        cantidad_personas=registro.cantidad_personas,
        observaciones=registro.observaciones,
        mensaje="Entrada registrada correctamente",
    )


@router.put("/{registro_id}/salida", response_model=RegistroVisitanteResponse)
def registrar_salida(
    registro_id: int,
    payload: SalidaVisitanteRequest,
    db: Session = Depends(get_db),
    _: Usuario = Depends(get_current_user),
) -> RegistroVisitanteResponse:
    """Register visitor exit."""
    registro = db.query(RegistroVisitante).filter(RegistroVisitante.id == registro_id).first()
    if registro is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Registro no encontrado")
    if registro.fecha_salida is not None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Salida ya registrada")
    playa = db.query(Playa).filter(Playa.id == registro.playa_id).first()
    registro.fecha_salida = payload.fecha_salida or datetime.utcnow()
    db.commit()
    db.refresh(registro)
    return RegistroVisitanteResponse(
        id=registro.id,
        playa_id=registro.playa_id,
        playa_nombre=playa.nombre if playa else None,
        usuario_id=registro.usuario_id,
        fecha_entrada=registro.fecha_entrada,
        fecha_salida=registro.fecha_salida,
        cantidad_personas=registro.cantidad_personas,
        observaciones=registro.observaciones,
        mensaje="Salida registrada correctamente",
    )


@router.get("/activos/{playa_id}", response_model=OcupacionResponse)
def get_visitantes_activos(
    playa_id: int,
    db: Session = Depends(get_db),
    _: Usuario = Depends(get_current_user),
) -> OcupacionResponse:
    """Get current occupancy for a beach."""
    playa = db.query(Playa).filter(Playa.id == playa_id).first()
    if playa is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Playa no encontrada")
    registros = (
        db.query(RegistroVisitante)
        .filter(RegistroVisitante.playa_id == playa_id, RegistroVisitante.fecha_salida.is_(None))
        .all()
    )
    return OcupacionResponse(
        playa_id=playa.id,
        playa_nombre=playa.nombre,
        total_visitantes=obtener_visitantes_activos(db, playa_id),
        registros_activos=len(registros),
        fecha_consulta=datetime.utcnow(),
    )
