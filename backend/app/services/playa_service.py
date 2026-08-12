"""Beach access helpers with row-level locking."""

from sqlalchemy.orm import Session

from app.models import Playa


def get_playa_for_update(db: Session, playa_id: int) -> Playa | None:
    """Return a beach row locked for update."""
    return db.query(Playa).filter(Playa.id == playa_id).with_for_update().first()


def get_active_playa_for_update(db: Session, playa_id: int) -> Playa | None:
    """Return an active beach row locked for update."""
    return (
        db.query(Playa)
        .filter(Playa.id == playa_id, Playa.activa.is_(True))
        .with_for_update()
        .first()
    )
