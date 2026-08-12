"""Shared domain enumerations."""

import enum


class RolUsuario(str, enum.Enum):
    """User roles."""

    INVESTIGADOR = "investigador"
    ADMINISTRADOR = "administrador"


class TipoEvento(str, enum.Enum):
    """Environmental event types."""

    ARRIBADA_TORTUGAS = "arribada_tortugas"
    MAREA_ROJA = "marea_roja"
    MAREA_ALTA = "marea_alta"
    CONDICION_CLIMATICA = "condicion_climatica"
    RESTRICCION_ACCESO = "restriccion_acceso"
    CIERRE_TEMPORAL = "cierre_temporal"
    OTRO = "otro"


class EstadoEvento(str, enum.Enum):
    """Environmental event approval lifecycle."""

    PENDIENTE = "pendiente"
    APROBADO = "aprobado"
    RECHAZADO = "rechazado"
    CERRADO = "cerrado"


class OrigenEvento(str, enum.Enum):
    """Who reported the environmental event."""

    VISITANTE = "visitante"
    INVESTIGADOR = "investigador"
    ADMINISTRADOR = "administrador"


class TipoAvisoPublico(str, enum.Enum):
    """Public announcement type for the main page."""

    EVENTO_PENDIENTE = "evento_pendiente"
    EVENTO_APROBADO = "evento_aprobado"
    EVENTO_CERRADO = "evento_cerrado"


class MetodoCcr(str, enum.Enum):
    """CCR calculation method."""

    FORMULA = "formula"
    MACHINE_LEARNING = "machine_learning"
    HIBRIDO = "hibrido"
