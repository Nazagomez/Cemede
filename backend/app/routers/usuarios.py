"""User administration routes (requires the usuarios.gestionar permission)."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.permissions import require_permission
from app.core.security import generar_password_temporal, hash_password
from app.database import get_db
from app.models import Usuario
from app.schemas import (
    UsuarioCreateRequest,
    UsuarioPasswordRequest,
    UsuarioResponse,
    UsuarioRolRequest,
)
from app.services.email_service import enviar_credenciales

router = APIRouter(prefix="/usuarios", tags=["Usuarios"])


def _get_usuario_or_404(db: Session, usuario_id: int) -> Usuario:
    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    if usuario is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado")
    return usuario


@router.get("", response_model=list[UsuarioResponse])
def list_usuarios(
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_permission("usuarios.gestionar")),
) -> list[UsuarioResponse]:
    """List all users."""
    usuarios = db.query(Usuario).order_by(Usuario.nombre).all()
    return [UsuarioResponse.model_validate(u) for u in usuarios]


@router.post("", response_model=UsuarioResponse, status_code=status.HTTP_201_CREATED)
def crear_usuario(
    payload: UsuarioCreateRequest,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_permission("usuarios.gestionar")),
) -> UsuarioResponse:
    """Create a new user with an auto-generated temporary password."""
    existe = db.query(Usuario).filter(Usuario.email == payload.email).first()
    if existe is not None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Ya existe un usuario con ese correo")

    password_temporal = generar_password_temporal()
    usuario = Usuario(
        nombre=payload.nombre,
        email=payload.email,
        password_hash=hash_password(password_temporal),
        rol=payload.rol,
        activo=True,
        debe_cambiar_password=True,
    )
    db.add(usuario)
    db.commit()
    db.refresh(usuario)

    enviado = enviar_credenciales(usuario.email, usuario.nombre, password_temporal)
    respuesta = UsuarioResponse.model_validate(usuario)
    respuesta.mensaje = (
        "Usuario creado. Se envió la contraseña temporal por correo."
        if enviado
        else f"Usuario creado, pero no se pudo enviar el correo. Contraseña temporal: {password_temporal} (comunicásela por otro medio)."
    )
    return respuesta


@router.put("/{usuario_id}/activo", response_model=UsuarioResponse)
def cambiar_estado_usuario(
    usuario_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_permission("usuarios.gestionar")),
) -> UsuarioResponse:
    """Toggle active/inactive status (not on your own account)."""
    usuario = _get_usuario_or_404(db, usuario_id)
    if usuario.id == current_user.id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No podés desactivar tu propia cuenta")
    usuario.activo = not usuario.activo
    db.commit()
    db.refresh(usuario)
    return UsuarioResponse.model_validate(usuario)


@router.put("/{usuario_id}/rol", response_model=UsuarioResponse)
def cambiar_rol_usuario(
    usuario_id: int,
    payload: UsuarioRolRequest,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_permission("usuarios.gestionar")),
) -> UsuarioResponse:
    """Change a user's role (not on your own account)."""
    usuario = _get_usuario_or_404(db, usuario_id)
    if usuario.id == current_user.id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No podés cambiar tu propio rol")
    usuario.rol = payload.rol
    db.commit()
    db.refresh(usuario)
    return UsuarioResponse.model_validate(usuario)


@router.put("/{usuario_id}/password", response_model=UsuarioResponse)
def resetear_password_usuario(
    usuario_id: int,
    payload: UsuarioPasswordRequest,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_permission("usuarios.gestionar")),
) -> UsuarioResponse:
    """Set a new password for a user. Also forces a change on next login."""
    usuario = _get_usuario_or_404(db, usuario_id)
    usuario.password_hash = hash_password(payload.password)
    usuario.debe_cambiar_password = True
    db.commit()
    db.refresh(usuario)
    return UsuarioResponse.model_validate(usuario)