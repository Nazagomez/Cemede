"""Configurable permission-based authorization."""

from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.database import get_db
from app.models import Permiso, RolPermiso, Usuario


def get_permisos_de_rol(db: Session, rol: str) -> list[str]:
    """Return the sorted list of permission keys granted to a role."""
    filas = (
        db.query(Permiso.clave)
        .join(RolPermiso, RolPermiso.permiso_id == Permiso.id)
        .filter(RolPermiso.rol == rol)
        .all()
    )
    return sorted(clave for (clave,) in filas)


def usuario_tiene_permiso(db: Session, rol: str, clave: str) -> bool:
    """Check whether a role currently has a given permission granted."""
    existe = (
        db.query(RolPermiso)
        .join(Permiso, Permiso.id == RolPermiso.permiso_id)
        .filter(RolPermiso.rol == rol, Permiso.clave == clave)
        .first()
    )
    return existe is not None


def require_permission(clave: str):
    """Build a FastAPI dependency requiring a specific configurable permission."""

    def dependency(
        db: Session = Depends(get_db),
        current_user: Usuario = Depends(get_current_user),
    ) -> Usuario:
        if not usuario_tiene_permiso(db, current_user.rol.value, clave):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permiso denegado")
        return current_user

    return dependency