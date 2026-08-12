"""Public announcement business logic."""

from sqlalchemy.orm import Session

from app.enums import TipoAvisoPublico
from app.models import AvisoPublico, Playa
from app.schemas import AvisoPublicoResponse


def build_aviso_publico_response(
    aviso: AvisoPublico,
    playa_nombre: str,
) -> AvisoPublicoResponse:
    """Build a public announcement API response."""
    return AvisoPublicoResponse(
        id=aviso.id,
        evento_id=aviso.evento_id,
        playa_id=aviso.playa_id,
        playa_nombre=playa_nombre,
        tipo=aviso.tipo,
        titulo=aviso.titulo,
        mensaje=aviso.mensaje,
        created_at=aviso.created_at,
    )


def create_public_aviso(
    db: Session,
    playa_id: int,
    titulo: str,
    mensaje: str,
    tipo: TipoAvisoPublico,
    evento_id: int | None = None,
) -> AvisoPublico:
    """Persist a public announcement for the main page."""
    aviso = AvisoPublico(
        evento_id=evento_id,
        playa_id=playa_id,
        tipo=tipo,
        titulo=titulo,
        mensaje=mensaje,
    )
    db.add(aviso)
    return aviso


def remove_public_avisos_for_evento(
    db: Session,
    evento_id: int,
    tipo: TipoAvisoPublico,
) -> None:
    """Remove stale public announcements for an event and announcement type."""
    db.query(AvisoPublico).filter(
        AvisoPublico.evento_id == evento_id,
        AvisoPublico.tipo == tipo,
    ).delete(synchronize_session=False)


def list_public_avisos(
    db: Session,
    playa_id: int | None = None,
    limit: int = 20,
) -> list[AvisoPublicoResponse]:
    """List recent public announcements."""
    query = db.query(AvisoPublico, Playa.nombre).join(Playa, Playa.id == AvisoPublico.playa_id)
    if playa_id is not None:
        query = query.filter(AvisoPublico.playa_id == playa_id)
    rows = query.order_by(AvisoPublico.created_at.desc()).limit(limit).all()
    return [
        build_aviso_publico_response(aviso, playa_nombre)
        for aviso, playa_nombre in rows
    ]
