"""CEMEDE field-validated CCF/CCE reference parameters (Doc 08 / Guayabo adaptation)."""

from dataclasses import dataclass


@dataclass(frozen=True)
class CcfFieldParams:
    """Validated carrying-capacity configuration for one beach."""

    playa_nombre: str
    area_util_m2: float
    area_por_visitante_m2: float
    periodo_horas: int
    tiempo_permanencia_horas: float
    capacidad_manejo: float
    fuente: str


CEMEDE_FIELD_CCF_PARAMS: dict[str, CcfFieldParams] = {
    "junquillal": CcfFieldParams(
        playa_nombre="Junquillal de la Cruz",
        area_util_m2=45000.0,
        area_por_visitante_m2=20.0,
        periodo_horas=8,
        tiempo_permanencia_horas=4.0,
        capacidad_manejo=0.7532,
        fuente="Refugio Nacional Bahía Junquillal; estándar recreativo 20 m²/visitante; CM referencia Guayabo (CEMEDE).",
    ),
    "playa_grande": CcfFieldParams(
        playa_nombre="Playa Grande",
        area_util_m2=32000.0,
        area_por_visitante_m2=15.0,
        periodo_horas=8,
        tiempo_permanencia_horas=3.5,
        capacidad_manejo=0.80,
        fuente="Parque Nacional Marino Las Baulas; mayor densidad costera; CM operativa CEMEDE.",
    ),
}
