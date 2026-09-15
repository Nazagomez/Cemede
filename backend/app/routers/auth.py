"""Authentication routes."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.core.permissions import get_permisos_de_rol
from app.core.security import create_access_token, hash_password, verify_password
from app.database import get_db
from app.models import Usuario
from app.schemas import CambiarPasswordRequest, LoginRequest, TokenResponse, UsuarioResponse

router = APIRouter(prefix="/auth", tags=["Autenticación"])


def _build_usuario_response(db: Session, usuario: Usuario) -> UsuarioResponse:
    permisos = get_permisos_de_rol(db, usuario.rol.value)
    return UsuarioResponse.model_validate(usuario).model_copy(update={"permisos": permisos})


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)) -> TokenResponse:
    """Authenticate user and return JWT."""
    user = db.query(Usuario).filter(Usuario.email == payload.email, Usuario.activo.is_(True)).first()
    if user is None or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Credenciales incorrectas")
    token = create_access_token(user.email)
    return TokenResponse(
        access_token=token,
        usuario=_build_usuario_response(db, user),
    )


@router.get("/me", response_model=UsuarioResponse)
def get_me(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
) -> UsuarioResponse:
    """Return current authenticated user with their current permissions."""
    return _build_usuario_response(db, current_user)


@router.put("/password", response_model=UsuarioResponse)
def cambiar_password(
    payload: CambiarPasswordRequest,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
) -> UsuarioResponse:
    """Set a new password for the current user and clear the forced-change flag."""
    current_user.password_hash = hash_password(payload.password_nueva)
    current_user.debe_cambiar_password = False
    db.commit()
    db.refresh(current_user)
    return _build_usuario_response(db, current_user)