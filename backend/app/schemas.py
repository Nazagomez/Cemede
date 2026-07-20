"""Pydantic schemas for API validation."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.enums import MetodoCcr, RolUsuario, TipoEvento


class LoginRequest(BaseModel):
    """Login payload."""

    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    """JWT login response."""

    access_token: str
    token_type: str = "bearer"
    usuario: "UsuarioResponse"


class UsuarioResponse(BaseModel):
    """Public user data."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    nombre: str
    email: EmailStr
    rol: RolUsuario
    activo: bool = True


class PlayaResponse(BaseModel):
    """Beach response."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    nombre: str
    descripcion: str | None
    area_util_m2: float
    canton: str
    provincia: str
    latitud: float | None
    longitud: float | None
    activa: bool


class ConfiguracionCcfResponse(BaseModel):
    """CCF configuration response."""

    model_config = ConfigDict(from_attributes=True)

    playa_id: int
    area_por_visitante_m2: float
    periodo_horas: int
    tiempo_permanencia_horas: float
    capacidad_manejo: float
    updated_at: datetime | None = None


class ConfiguracionCcfUpdate(BaseModel):
    """CCF configuration update payload."""

    area_por_visitante_m2: float = Field(gt=0)
    periodo_horas: int = Field(gt=0)
    tiempo_permanencia_horas: float = Field(gt=0)
    capacidad_manejo: float = Field(gt=0, le=1)


class EntradaVisitanteRequest(BaseModel):
    """Visitor entry payload."""

    playa_id: int
    cantidad_personas: int = Field(default=1, ge=1)
    observaciones: str | None = None


class RegistroVisitanteResponse(BaseModel):
    """Visitor record response."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    playa_id: int
    playa_nombre: str | None = None
    usuario_id: int
    fecha_entrada: datetime
    fecha_salida: datetime | None
    cantidad_personas: int
    observaciones: str | None = None
    mensaje: str | None = None


class SalidaVisitanteRequest(BaseModel):
    """Optional explicit exit datetime."""

    fecha_salida: datetime | None = None


class OcupacionResponse(BaseModel):
    """Current occupancy summary."""

    playa_id: int
    playa_nombre: str
    total_visitantes: int
    registros_activos: int
    fecha_consulta: datetime


class RegistroVisitanteHistorialItem(BaseModel):
    """Visitor record item for history listing."""

    id: int
    playa_id: int
    playa_nombre: str | None = None
    fecha_entrada: datetime
    fecha_salida: datetime | None
    cantidad_personas: int


class VisitanteHistorialResponse(BaseModel):
    """Paginated visitor history response."""

    total: int
    page: int
    limit: int
    registros: list[RegistroVisitanteHistorialItem]


class EventoAmbientalRequest(BaseModel):
    """Environmental event payload."""

    playa_id: int
    tipo: TipoEvento
    titulo: str
    descripcion: str | None = None
    fecha_inicio: datetime
    parte_afectada: float = Field(ge=0)
    totalidad_analizada: float = Field(gt=0)


class EventoAmbientalResponse(BaseModel):
    """Environmental event response."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    playa_id: int
    playa_nombre: str | None = None
    tipo: TipoEvento
    titulo: str
    descripcion: str | None
    fecha_inicio: datetime
    fecha_fin: datetime | None
    factor_correccion: float | None = None
    activo: bool
    mensaje: str | None = None


class CapacidadEstimacionResponse(BaseModel):
    """Full capacity estimation."""

    playa_id: int
    playa_nombre: str
    fecha_calculo: datetime
    ccf: float
    ccr_formula: float
    ccr_ml: float | None
    ccr_final: float
    cce: float
    metodo_ccr: MetodoCcr
    visitantes_actuales: int
    porcentaje_ocupacion: float
    eventos_activos: int
    estado: str


class DashboardPlayaResponse(BaseModel):
    """Dashboard summary for one beach."""

    playa: PlayaResponse
    ocupacion: dict[str, float | int | str]
    capacidad: dict[str, float | str | None]
    eventos_activos: list[dict[str, float | int | str]]
    ultimas_estimaciones: list[dict[str, float | str]]


class MessageResponse(BaseModel):
    """Generic message response."""

    mensaje: str
