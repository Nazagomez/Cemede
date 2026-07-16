# Fórmulas de Capacidad de Carga Turística (CCF, CCR, CCE)

**Proyecto:** Sistema web CEMEDE-UNA — Capacidad de carga turística  
**Fuente metodológica:** Cifuentes Arias, M., et al. (1999). *Capacidad de carga turística de las áreas de uso público del Monumento Nacional Guayabo, Costa Rica*. WWF Centroamérica / CATIE.  
**URL:** [Documento Guayabo (PDF)](https://awsassets.panda.org/downloads/wwfca_guayabo.pdf)

---

## 1. Marco conceptual (según Cifuentes et al., 1999)

La capacidad de carga turística no es un valor único y estático. Se determina en **tres niveles progresivos**:

```
CCF  →  CCR  →  CCE
(física)  (real)  (efectiva)
```

| Nivel | Sigla | Significado |
|---|---|---|
| Capacidad de Carga Física | **CCF** | Límite teórico según espacio disponible, horario y tiempo de permanencia |
| Capacidad de Carga Real | **CCR** | CCF ajustada por condiciones ambientales, físicas y sociales del sitio |
| Capacidad de Carga Efectiva | **CCE** | CCR ajustada por la capacidad administrativa y operativa de manejo |

**Relación general:**

```
CCF ≥ CCR ≥ CCE
```

---

## 2. Fórmulas oficiales del documento Guayabo

### 2.1 Capacidad de Carga Física (CCF)

**Definición (Guayabo, sección 7.2):**  
Es el límite máximo de visitas que se pueden hacer al sitio durante un día.

**Fórmula para senderos (metros lineales):**

```
CCF = S × NV
```

Donde:

| Variable | Descripción |
|---|---|
| **S** | Superficie disponible (metros lineales del sendero) |
| **NV** | Número de veces que el sitio puede ser visitado por la misma persona en un día |
| **NV** | `Hv / tv` |
| **Hv** | Horario de visita (horas/día que el sitio está abierto) |
| **tv** | Tiempo necesario para visitar el sitio (horas) |

**Ejemplo Guayabo — Sendero Los Montículos:**

| Parámetro | Valor |
|---|---|
| S | 1.470 m |
| Hv | 8 h/día (8:00–16:00) |
| tv | 1,5 h |
| NV | 8 / 1,5 = **5,33 visitas/día/visitante** |

```
CCF = 1.470 × 5,33 = 7.834,51 visitas/día
```

**Ejemplo Guayabo — Sendero Natural:**

```
S = 2.054,53 m
CCF = 2.054,53 × 5,33 = 10.950,64 visitas/día
```

---

### 2.2 Adaptación de CCF para playas (área en m²)

En playas no se usa longitud lineal, sino **área útil**. La adaptación equivalente es:

```
CCF = (A / ap) × (Hv / tv)
```

Donde:

| Variable | Descripción |
|---|---|
| **A** | Área útil de la playa (m²) |
| **ap** | Área requerida por visitante (m²/persona) |
| **Hv** | Horario de visita (horas/día) |
| **tv** | Tiempo promedio de permanencia (horas) |

**Equivalencia con la fórmula de Guayabo:**

| Guayabo (senderos) | Playas (costa) |
|---|---|
| S = metros lineales | A / ap = capacidad física de personas simultáneas |
| NV = Hv / tv | NV = Hv / tv (igual) |
| CCF = S × NV | CCF = (A / ap) × NV |

> Esta adaptación mantiene la lógica de Cifuentes (1992, 1999): relacionar **espacio disponible**, **espacio por persona** y **rotación de visitantes** en el periodo analizado.

---

### 2.3 Factor de corrección general (FC)

**Fórmula general (Guayabo, sección 7.3):**

```
FCx = 1 - (Mlx / Mtx)
```

Donde:

| Variable | Descripción |
|---|---|
| **FCx** | Factor de corrección por la variable "x" |
| **Mlx** | Magnitud limitante de la variable "x" |
| **Mtx** | Magnitud total analizada de la variable "x" |

**Interpretación:**  
Si el 25% del área está restringida por marea alta:

```
FC = 1 - (0,25) = 0,75
```

Es decir, solo el 75% de la capacidad física puede usarse bajo esa condición.

**Variante con ponderación (Guayabo — erodabilidad y accesibilidad):**

Cuando hay grados de limitación (medio/alto):

```
FC = 1 - ((ma × 1,5) + (mm × 1)) / mt
```

Donde **ma** = magnitud con limitación alta, **mm** = magnitud con limitación media.

> Para el sistema CEMEDE en playas, se usa la **fórmula general simple** `FC = 1 - (Mlx/Mtx)` salvo que el estudio de campo defina ponderaciones específicas.

---

### 2.4 Capacidad de Carga Real (CCR)

**Fórmula (Guayabo, sección 7.3.1):**

```
CCR = CCF × FC1 × FC2 × FC3 × ... × FCn
```

Los factores de corrección se **multiplican** entre sí.

**Ejemplo Guayabo — Sendero Los Montículos:**

```
CCR = CCF × FCsoc × FCero × FCacc × FCpre × FCsol × FCtem
```

| Factor | Valor (Tabla 1, Guayabo) |
|---|---|
| CCF | 7.834,51 |
| FCsoc | 0,2309 |
| FCero | 0,9545 |
| FCacc | 0,6547 |
| FCpre | 0,6233 |
| FCsol | 0,8893 |
| FCtem | 0,8575 |

**Cálculo paso a paso:**

```
CCR = 7.834,51 × 0,2309 × 0,9545 × 0,6547 × 0,6233 × 0,8893 × 0,8575
CCR = 537,32 visitas/día
```

**Verificación:**

| Paso | Operación | Resultado parcial |
|---|---|---|
| 1 | 7.834,51 × 0,2309 | 1.808,99 |
| 2 | × 0,9545 | 1.726,68 |
| 3 | × 0,6547 | 1.129,95 |
| 4 | × 0,6233 | 704,10 |
| 5 | × 0,8893 | 626,06 |
| 6 | × 0,8575 | **537,32** ✓ |

**Regla de limitante crítica (Guayabo, sección 7.5):**  
Si el sitio tiene varias zonas conectadas, la **CCR menor** entre zonas constituye la limitante crítica para todo el sitio.

---

### 2.5 Capacidad de Manejo (CM)

**Definición (Guayabo, sección 7.4):**  
Conjunto de condiciones administrativas, de infraestructura, personal y equipamiento para gestionar el uso turístico.

**Fórmula:**

```
CM = ((Factor_Infraestructura + Factor_Equipo + Factor_Personal) / 3) × 100
```

**Ejemplo Guayabo:**

| Variable | Factor |
|---|---|
| Infraestructura | 0,7543 |
| Equipo | 0,8802 |
| Personal | 0,6250 |

```
CM = ((0,7543 + 0,8802 + 0,6250) / 3) × 100
CM = (2,2595 / 3) × 100
CM = 75,32%
```

En decimal para cálculos: **CM = 0,7532**

---

### 2.6 Capacidad de Carga Efectiva (CCE)

**Fórmula (Guayabo, sección 7.5):**

```
CCE = CCR × CM
```

**Ejemplo Guayabo:**

```
CCE = 537,32 × 0,7532
CCE = 404,71 visitas/día
```

**Visitantes únicos por día (Guayabo, sección 8.2):**

```
Visitantes/día = CCE / NV
Visitantes/día = 404,71 / 5,33 = 76 visitantes/día
Visitantes/año = 76 × 365 = 27.714 visitantes/año
```

---

## 3. Factores de corrección aplicables a playas costeras

Guayabo usa factores propios de senderos (FCsoc, FCero, FCacc, FCpre, FCsol, FCtem, FCane).  
Para **Junquillal** y **Playa Grande**, el sistema CEMEDE adapta variables costeras:

| Variable | Código sugerido | Mlx (limitante) | Mtx (total) | Ejemplo |
|---|---|---|---|---|
| Marea alta | FC_marea | Área inundada en marea alta | Área útil total | m² afectados / m² totales |
| Arribada de tortugas | FC_tortugas | Zona de anidación restringida | Área útil total | sector restringido |
| Marea roja | FC_marea_roja | Área con restricción sanitaria | Área útil total | cierre parcial |
| Condición climática | FC_clima | Horas con clima adverso | Horas de visita anuales | como FCpre en Guayabo |
| Restricción de acceso | FC_acceso | Área con acceso limitado | Área útil total | senderos cerrados |
| Cierre temporal | FC_cierre | Horas/días cerrados | Horas/días totales | como FCtem en Guayabo |

**En todos los casos:**

```
FCx = 1 - (Mlx / Mtx)
```

---

## 4. Ejemplos numéricos — Junquillal de la Cruz

### 4.1 Parámetros de referencia

| Parámetro | Valor | Fuente / nota |
|---|---|---|
| Área útil (A) | 45.000 m² | Refugio Nacional de Vida Silvestre Bahía Junquillal |
| Área por visitante (ap) | 20 m²/persona | Estándar recreativo playa (Cifuentes, 1992) |
| Horario visita (Hv) | 8 h/día | 6:00–14:00 (referencia) |
| Tiempo permanencia (tv) | 4,0 h | Estimación sector costero |
| Capacidad de manejo (CM) | 75,32% | Referencia Guayabo (ajustable con estudio CEMEDE) |

### 4.2 Cálculo CCF

```
NV = Hv / tv = 8 / 4,0 = 2,0 visitas/día/visitante

CCF = (A / ap) × NV
CCF = (45.000 / 20) × 2,0
CCF = 2.250 × 2,0
CCF = 4.500 visitas/día
```

### 4.3 Factores de corrección (escenario de ejemplo)

| Evento | Mlx | Mtx | FC = 1 - (Mlx/Mtx) |
|---|---|---|---|
| Marea alta (sector sur) | 5.000 m² | 45.000 m² | 1 - 0,1111 = **0,8889** |
| Restricción acceso (sendero) | 4.500 m² | 45.000 m² | 1 - 0,1000 = **0,9000** |
| Precipitación (horas lluvia) | 1.100 h | 2.920 h | 1 - 0,3767 = **0,6233** |

> El factor de precipitación usa la misma lógica que **FCpre** en Guayabo: horas limitantes / horas totales de operación anual.

### 4.4 Cálculo CCR

```
CCR = CCF × FC_marea × FC_acceso × FC_precipitacion
CCR = 4.500 × 0,8889 × 0,9000 × 0,6233
CCR = 2.241,47 visitas/día
```

**Cálculo paso a paso:**

| Paso | Operación | Resultado |
|---|---|---|
| 1 | 4.500 × 0,8889 | 3.999,05 |
| 2 | × 0,9000 | 3.599,15 |
| 3 | × 0,6233 | **2.241,47** |

### 4.5 Cálculo CCE

```
CCE = CCR × CM
CCE = 2.241,47 × 0,7532
CCE = 1.688,28 visitas/día
```

### 4.6 Ocupación actual (ejemplo operativo del sistema)

Supongamos que hay **87 visitantes** registrados actualmente en la playa:

```
Visitantes actuales = 87
Ocupación % = (87 / CCR) × 100
Ocupación % = (87 / 2.241,47) × 100
Ocupación % = 3,88%  →  Estado: NORMAL (< 70%)
```

---

## 5. Ejemplos numéricos — Playa Grande

### 5.1 Parámetros de referencia

| Parámetro | Valor | Fuente / nota |
|---|---|---|
| Área útil (A) | 32.000 m² | Parque Nacional Marino Las Baulas |
| Área por visitante (ap) | 15 m²/persona | Mayor densidad, playa más transitada |
| Horario visita (Hv) | 8 h/día | Horario diurno |
| Tiempo permanencia (tv) | 3,5 h | Permanencia promedio estimada |
| Capacidad de manejo (CM) | 80,00% | Mejor infraestructura de manejo (SINAC) |

### 5.2 Cálculo CCF

```
NV = Hv / tv = 8 / 3,5 = 2,286 visitas/día/visitante

CCF = (A / ap) × NV
CCF = (32.000 / 15) × 2,286
CCF = 2.133,33 × 2,286
CCF = 4.876,19 visitas/día
```

### 5.3 Factores de corrección (escenario de ejemplo)

| Evento | Mlx | Mtx | FC = 1 - (Mlx/Mtx) |
|---|---|---|---|
| Arribada tortugas (zona anidación) | 8.000 m² | 32.000 m² | 1 - 0,2500 = **0,7500** |
| Marea alta | 4.000 m² | 32.000 m² | 1 - 0,1250 = **0,8750** |
| Cierre temporal (lunes) | 416 h/año | 2.920 h/año | 1 - 0,1425 = **0,8575** |

> El factor de cierre temporal replica **FCtem** de Guayabo.

### 5.4 Cálculo CCR

```
CCR = CCF × FC_tortugas × FC_marea × FC_cierre
CCR = 4.876,19 × 0,7500 × 0,8750 × 0,8575
CCR = 2.741,47 visitas/día
```

**Cálculo paso a paso:**

| Paso | Operación | Resultado |
|---|---|---|
| 1 | 4.876,19 × 0,7500 | 3.657,14 |
| 2 | × 0,8750 | 3.200,00 |
| 3 | × 0,8575 | **2.741,47** |

### 5.5 Cálculo CCE

```
CCE = CCR × CM
CCE = 2.741,47 × 0,80
CCE = 2.193,18 visitas/día
```

### 5.6 Ocupación actual (ejemplo operativo)

Con **45 visitantes** actuales:

```
Ocupación % = (45 / 2.741,47) × 100
Ocupación % = 1,64%  →  Estado: NORMAL
```

---

## 6. Tabla comparativa resumen

| Indicador | Junquillal | Playa Grande | Guayabo (ref.) |
|---|---|---|---|
| **CCF** | 4.500 visitas/día | 4.876 visitas/día | 7.834 visitas/día |
| **CCR** | 2.241 visitas/día | 2.741 visitas/día | 537 visitas/día |
| **CM** | 75,32% | 80,00% | 75,32% |
| **CCE** | 1.688 visitas/día | 2.193 visitas/día | 405 visitas/día |
| **Visitantes actuales (ej.)** | 87 | 45 | — |
| **Ocupación % (ej.)** | 3,88% | 1,64% | — |

---

## 7. Estados de ocupación del sistema

| Estado | Condición | Acción sugerida |
|---|---|---|
| **Normal** | Ocupación < 70% de CCR | Monitoreo rutinario |
| **Advertencia** | Ocupación 70% – 90% | Alerta a investigadores CEMEDE |
| **Crítico** | Ocupación > 90% | Notificación urgente, posible restricción |

**Fórmula en el sistema:**

```
porcentaje_ocupacion = (visitantes_actuales / ccr_final) × 100
```

---

## 8. Implementación en el backend (FastAPI)

### 8.1 Servicio CCF

```python
def calcular_ccf(area_util: float, area_por_visitante: float,
                 periodo_horas: float, tiempo_permanencia: float) -> float:
    nv = periodo_horas / tiempo_permanencia
    ccf = (area_util / area_por_visitante) * nv
    return round(ccf, 2)
```

### 8.2 Servicio factor de corrección

```python
def calcular_factor_correccion(magnitud_limitante: float,
                               magnitud_total: float) -> float:
    if magnitud_total <= 0:
        return 1.0
    fc = 1 - (magnitud_limitante / magnitud_total)
    return round(max(fc, 0), 4)
```

### 8.3 Servicio CCR

```python
def calcular_ccr(ccf: float, factores: list[float]) -> float:
    ccr = ccf
    for fc in factores:
        ccr *= fc
    return round(ccr, 2)
```

### 8.4 Servicio CCE

```python
def calcular_cce(ccr: float, capacidad_manejo: float) -> float:
    cce = ccr * capacidad_manejo
    return round(cce, 2)
```

### 8.5 Servicio ocupación

```python
def calcular_ocupacion(visitantes_actuales: int, ccr: float) -> dict:
    porcentaje = (visitantes_actuales / ccr) * 100 if ccr > 0 else 0
    if porcentaje < 70:
        estado = "normal"
    elif porcentaje <= 90:
        estado = "advertencia"
    else:
        estado = "critico"
    return {
        "visitantes_actuales": visitantes_actuales,
        "porcentaje_ocupacion": round(porcentaje, 2),
        "estado": estado
    }
```

---

## 9. Relación con el módulo ML

El ML **no reemplaza** estas fórmulas. Las complementa:

| Método | Cuándo se usa | Variable en BD |
|---|---|---|
| Fórmula Cifuentes | Siempre (método base) | `ccr_formula` |
| ML (DecisionTreeRegressor) | Cuando hay datos suficientes | `ccr_ml` |
| Valor final | Fórmula por defecto; ML si hay modelo | `ccr_final` |

```
Si modelo_ml_activo y registros >= 50:
    ccr_final = ccr_ml
Sino:
    ccr_final = ccr_formula
```

---

## 10. Referencia bibliográfica

Cifuentes Arias, M., Mesquita, C. A. B., Méndez, J., Morales, M. E., Aguilar, N., Cancino, D., Gallo, M., Jolón, M., Ramírez, C., Ribeiro, N., Sandoval, E., & Turcios, M. (1999). *Capacidad de carga turística de las áreas de uso público del Monumento Nacional Guayabo, Costa Rica*. WWF Centroamérica & CATIE. https://awsassets.panda.org/downloads/wwfca_guayabo.pdf

---

## 11. Notas para el Doc 08

1. Los parámetros de Junquillal y Playa Grande son **valores de referencia** para el sistema; deben validarse con CEMEDE en campo.
2. Los factores de corrección de los ejemplos son **escenarios ilustrativos** basados en la lógica del documento Guayabo.
3. La metodología original usa senderos; aquí se **adapta a playas** manteniendo la estructura CCF → CCR → CCE.
4. El cálculo de CM puede refinarse con la escala 0–4 del Anexo 3 de Guayabo cuando CEMEDE disponga de datos de infraestructura, personal y equipamiento.

---

*Documento de diseño — Doc 08 · Fórmulas de capacidad de carga turística*
