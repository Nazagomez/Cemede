"""SQLAlchemy ORM models."""

from datetime import datetime

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.enums import MetodoCcr, RolUsuario, TipoEvento


class Usuario(Base):
    """System user."""

    __tablename__ = "usuario"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nombre: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(150), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    rol: Mapped[RolUsuario] = mapped_column(Enum(RolUsuario), nullable=False, default=RolUsuario.INVESTIGADOR)
    activo: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)


class Playa(Base):
    """Beach site."""

    __tablename__ = "playa"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nombre: Mapped[str] = mapped_column(String(150), nullable=False)
    descripcion: Mapped[str | None] = mapped_column(Text)
    area_util_m2: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    canton: Mapped[str] = mapped_column(String(100), nullable=False)
    provincia: Mapped[str] = mapped_column(String(100), nullable=False, default="Guanacaste")
    latitud: Mapped[float | None] = mapped_column(Numeric(10, 7))
    longitud: Mapped[float | None] = mapped_column(Numeric(10, 7))
    activa: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    configuracion: Mapped["ConfiguracionCcf"] = relationship(back_populates="playa", uselist=False)


class ConfiguracionCcf(Base):
    """CCF/CCE parameters per beach."""

    __tablename__ = "configuracion_ccf"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    playa_id: Mapped[int] = mapped_column(ForeignKey("playa.id"), unique=True, nullable=False)
    area_por_visitante_m2: Mapped[float] = mapped_column(Numeric(8, 2), nullable=False)
    periodo_horas: Mapped[int] = mapped_column(Integer, nullable=False, default=8)
    tiempo_permanencia_horas: Mapped[float] = mapped_column(Numeric(5, 2), nullable=False)
    capacidad_manejo: Mapped[float] = mapped_column(Numeric(4, 2), nullable=False, default=0.75)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    playa: Mapped[Playa] = relationship(back_populates="configuracion")


class RegistroVisitante(Base):
    """Visitor entry/exit record."""

    __tablename__ = "registro_visitante"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    playa_id: Mapped[int] = mapped_column(ForeignKey("playa.id"), nullable=False)
    usuario_id: Mapped[int] = mapped_column(ForeignKey("usuario.id"), nullable=False)
    fecha_entrada: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    fecha_salida: Mapped[datetime | None] = mapped_column(DateTime)
    cantidad_personas: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    observaciones: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)


class EventoAmbiental(Base):
    """Environmental event affecting carrying capacity."""

    __tablename__ = "evento_ambiental"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    playa_id: Mapped[int] = mapped_column(ForeignKey("playa.id"), nullable=False)
    usuario_id: Mapped[int] = mapped_column(ForeignKey("usuario.id"), nullable=False)
    tipo: Mapped[TipoEvento] = mapped_column(Enum(TipoEvento), nullable=False)
    titulo: Mapped[str] = mapped_column(String(200), nullable=False)
    descripcion: Mapped[str | None] = mapped_column(Text)
    fecha_inicio: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    fecha_fin: Mapped[datetime | None] = mapped_column(DateTime)
    parte_afectada: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    totalidad_analizada: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    activo: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    factores: Mapped[list["FactorCorreccion"]] = relationship(back_populates="evento")


class FactorCorreccion(Base):
    """Correction factor derived from an environmental event."""

    __tablename__ = "factor_correccion"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    evento_id: Mapped[int] = mapped_column(ForeignKey("evento_ambiental.id"), nullable=False)
    nombre_variable: Mapped[str] = mapped_column(String(100), nullable=False)
    valor: Mapped[float] = mapped_column(Numeric(6, 4), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    evento: Mapped[EventoAmbiental] = relationship(back_populates="factores")


class EstimacionCapacidad(Base):
    """Historical capacity estimation record."""

    __tablename__ = "estimacion_capacidad"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    playa_id: Mapped[int] = mapped_column(ForeignKey("playa.id"), nullable=False)
    fecha_calculo: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    ccf: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    ccr_formula: Mapped[float | None] = mapped_column(Numeric(10, 2))
    ccr_ml: Mapped[float | None] = mapped_column(Numeric(10, 2))
    ccr_final: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    cce: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    visitantes_actuales: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    porcentaje_ocupacion: Mapped[float] = mapped_column(Numeric(6, 2), nullable=False, default=0)
    metodo_ccr: Mapped[MetodoCcr] = mapped_column(Enum(MetodoCcr), nullable=False, default=MetodoCcr.FORMULA)


class Notificacion(Base):
    """User notification."""

    __tablename__ = "notificacion"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    usuario_id: Mapped[int] = mapped_column(ForeignKey("usuario.id"), nullable=False)
    evento_id: Mapped[int | None] = mapped_column(ForeignKey("evento_ambiental.id"))
    playa_id: Mapped[int] = mapped_column(ForeignKey("playa.id"), nullable=False)
    titulo: Mapped[str] = mapped_column(String(200), nullable=False)
    mensaje: Mapped[str] = mapped_column(Text, nullable=False)
    leida: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
