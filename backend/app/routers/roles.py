"""Role permission management routes (requires usuarios.gestionar)."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.permissions import require_permission
from app.database import get_db
from app.enums import RolUsuario
from app.models import Permiso, RolPermiso, Usuario
from app.schemas import PermisoResponse, RolPermisosResponse, RolPermisosUpdateRequest

router = APIRouter(prefix="/roles", tags=["Roles"])


@router.get("/permisos", response_model=list[PermisoResponse])
def list_permisos_catalogo(
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_permission("usuarios.gestionar")),
) -> list[PermisoResponse]:
    """List the full catalog of available permissions."""
    return [PermisoResponse.model_validate(p) for p in db.query(Permiso).order_by(Permiso.id).all()]


@router.get("", response_model=list[RolPermisosResponse])
def list_roles(
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_permission("usuarios.gestionar")),
) -> list[RolPermisosResponse]:
    """List the 3 fixed roles with their currently granted permission keys."""
    filas = (
        db.query(RolPermiso.rol, Permiso.clave)
        .join(Permiso, Permiso.id == RolPermiso.permiso_id)
        .all()
    )
    permisos_por_rol: dict[str, list[str]] = {rol.value: [] for rol in RolUsuario}
    for rol, clave in filas:
        permisos_por_rol.setdefault(rol.value, []).append(clave)
    return [RolPermisosResponse(rol=rol, permisos=permisos_por_rol.get(rol.value, [])) for rol in RolUsuario]


@router.put("/{rol}/permisos", response_model=RolPermisosResponse)
def actualizar_permisos_rol(
    rol: RolUsuario,
    payload: RolPermisosUpdateRequest,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_permission("usuarios.gestionar")),
) -> RolPermisosResponse:
    """Replace the full set of permissions granted to a role (Administrador is protected)."""
    if rol == RolUsuario.ADMINISTRADOR:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El rol Administrador no es editable — siempre mantiene todos los permisos.",
        )

    permisos_validos = db.query(Permiso).filter(Permiso.clave.in_(payload.permisos)).all()
    claves_validas = {p.clave for p in permisos_validos}
    desconocidas = set(payload.permisos) - claves_validas
    if desconocidas:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Permisos desconocidos: {', '.join(desconocidas)}")

    db.query(RolPermiso).filter(RolPermiso.rol == rol).delete()
    db.add_all([RolPermiso(rol=rol, permiso_id=p.id) for p in permisos_validos])
    db.commit()

    return RolPermisosResponse(rol=rol, permisos=sorted(claves_validas))