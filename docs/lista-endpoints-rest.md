# Lista de Endpoints REST

**Proyecto:** Sistema web para la estimación de la capacidad de carga turística  
**Programa:** CEMEDE-UNA  
**Playas:** Junquillal de la Cruz y Playa Grande, Guanacaste  
**Stack:** React (frontend) · FastAPI (backend) · MySQL (base de datos)  
**Versión API:** v1  
**Prefijo base:** `/api`

---

## 1. Convenciones generales

| Aspecto | Detalle |
|---|---|
| Formato de intercambio | JSON |
| Autenticación | JWT Bearer Token |
| Header de autenticación | `Authorization: Bearer {token}` |
| Codificación | UTF-8 |
| Formato de fechas | ISO 8601 (`YYYY-MM-DDTHH:mm:ss`) |

### Códigos de respuesta HTTP

| Código | Significado |
|---|---|
| 200 | OK — Operación exitosa |
| 201 | Created — Recurso creado |
| 400 | Bad Request — Datos inválidos |
| 401 | Unauthorized — Token inválido o ausente |
| 403 | Forbidden — Sin permisos |
| 404 | Not Found — Recurso no encontrado |
| 500 | Internal Server Error — Error del servidor |

### Roles de usuario

| Rol | Descripción |
|---|---|
| `investigador` | Registra visitantes, reporta eventos, consulta dashboard |
| `administrador` | Gestiona configuración, usuarios y entrenamiento ML |

---

## 2. Resumen de endpoints (MVP)

| # | Método | Endpoint | Descripción | Auth |
|---|---|---|---|---|
| 1 | POST | `/api/auth/login` | Iniciar sesión | No |
| 2 | GET | `/api/auth/me` | Obtener usuario autenticado | Sí |
| 3 | GET | `/api/playas` | Listar playas | Sí |
| 4 | GET | `/api/playas/{id}` | Detalle de una playa | Sí |
| 5 | GET | `/api/playas/{id}/configuracion` | Parámetros CCF/CCE | Sí |
| 6 | PUT | `/api/playas/{id}/configuracion` | Actualizar parámetros | Admin |
| 7 | POST | `/api/visitantes/entrada` | Registrar entrada | Sí |
| 8 | PUT | `/api/visitantes/{id}/salida` | Registrar salida | Sí |
| 9 | GET | `/api/visitantes/activos/{playa_id}` | Ocupación actual por playa | Sí |
| 10 | GET | `/api/visitantes/historial` | Histórico de registros | Sí |
| 11 | POST | `/api/eventos` | Reportar evento ambiental | Sí |
| 12 | GET | `/api/eventos` | Listar eventos | Sí |
| 13 | GET | `/api/eventos/activos/{playa_id}` | Eventos activos por playa | Sí |
| 14 | PUT | `/api/eventos/{id}/cerrar` | Cerrar evento | Sí |
| 15 | GET | `/api/capacidad/estimacion/{playa_id}` | Estimación CCF, CCR, CCE | Sí |
| 16 | GET | `/api/capacidad/historial/{playa_id}` | Histórico de estimaciones | Sí |
| 17 | GET | `/api/dashboard/{playa_id}` | Panel resumen por playa | Sí |
| 18 | GET | `/api/dashboard` | Panel resumen general | Sí |
| 19 | GET | `/api/notificaciones` | Listar notificaciones | Sí |
| 20 | PUT | `/api/notificaciones/{id}/leida` | Marcar notificación leída | Sí |
| 21 | GET | `/api/ml/estado/{playa_id}` | Estado del modelo ML | Sí |
| 22 | POST | `/api/ml/entrenar/{playa_id}` | Entrenar modelo ML | Admin |
| 23 | GET | `/api/ml/prediccion/{playa_id}` | Predicción CCR por ML | Sí |

---

## 3. Estructura de rutas

```
/api
├── /auth
│   ├── POST   /login
│   └── GET    /me
│
├── /playas
│   ├── GET    /
│   ├── GET    /{id}
│   ├── GET    /{id}/configuracion
│   └── PUT    /{id}/configuracion
│
├── /visitantes
│   ├── POST   /entrada
│   ├── PUT    /{id}/salida
│   ├── GET    /activos/{playa_id}
│   └── GET    /historial
│
├── /eventos
│   ├── POST   /
│   ├── GET    /
│   ├── GET    /activos/{playa_id}
│   ├── PUT    /{id}/cerrar
│   └── GET    /{id}/factores
│
├── /capacidad
│   ├── GET    /ccf/{playa_id}
│   ├── GET    /ccr/{playa_id}
│   ├── GET    /cce/{playa_id}
│   ├── GET    /estimacion/{playa_id}
│   ├── GET    /historial/{playa_id}
│   └── POST   /calcular/{playa_id}
│
├── /dashboard
│   ├── GET    /
│   └── GET    /{playa_id}
│
├── /notificaciones
│   ├── GET    /
│   └── PUT    /{id}/leida
│
└── /ml
    ├── GET    /estado/{playa_id}
    ├── POST   /entrenar/{playa_id}
    └── GET    /prediccion/{playa_id}
```

---

## 4. Detalle por módulo

### 4.1 Autenticación

#### POST `/api/auth/login`

Inicia sesión de un investigador o administrador.

**Autenticación:** No requerida

**Request Body:**

```json
{
  "email": "investigador@una.ac.cr",
  "password": "123456"
}
```

**Response 200:**

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "usuario": {
    "id": 1,
    "nombre": "Yeilin Moya Baltodano",
    "email": "investigador@una.ac.cr",
    "rol": "investigador"
  }
}
```

**Response 401:**

```json
{
  "detail": "Credenciales incorrectas"
}
```

---

#### GET `/api/auth/me`

Retorna la información del usuario autenticado.

**Autenticación:** Requerida

**Response 200:**

```json
{
  "id": 1,
  "nombre": "Yeilin Moya Baltodano",
  "email": "investigador@una.ac.cr",
  "rol": "investigador",
  "activo": true
}
```

---

### 4.2 Playas

#### GET `/api/playas`

Lista todas las playas registradas en el sistema.

**Autenticación:** Requerida

**Response 200:**

```json
[
  {
    "id": 1,
    "nombre": "Junquillal de la Cruz",
    "descripcion": "Refugio Nacional de Vida Silvestre Bahía Junquillal",
    "area_util_m2": 45000.00,
    "canton": "La Cruz",
    "provincia": "Guanacaste",
    "latitud": 11.0300,
    "longitud": -85.7200,
    "activa": true
  },
  {
    "id": 2,
    "nombre": "Playa Grande",
    "descripcion": "Parque Nacional Marino Las Baulas",
    "area_util_m2": 32000.00,
    "canton": "Santa Cruz",
    "provincia": "Guanacaste",
    "latitud": 10.3400,
    "longitud": -85.8400,
    "activa": true
  }
]
```

---

#### GET `/api/playas/{id}`

Obtiene el detalle de una playa específica.

**Autenticación:** Requerida

**Parámetros de ruta:**

| Parámetro | Tipo | Descripción |
|---|---|---|
| id | int | ID de la playa |

**Response 200:**

```json
{
  "id": 1,
  "nombre": "Junquillal de la Cruz",
  "descripcion": "Refugio Nacional de Vida Silvestre Bahía Junquillal",
  "area_util_m2": 45000.00,
  "canton": "La Cruz",
  "provincia": "Guanacaste",
  "latitud": 11.0300,
  "longitud": -85.7200,
  "activa": true
}
```

---

#### GET `/api/playas/{id}/configuracion`

Obtiene los parámetros de configuración para el cálculo de CCF y CCE.

**Autenticación:** Requerida

**Response 200:**

```json
{
  "playa_id": 1,
  "area_por_visitante_m2": 20.00,
  "periodo_horas": 8,
  "tiempo_permanencia_horas": 4.0,
  "capacidad_manejo": 0.75,
  "updated_at": "2026-07-14T10:00:00"
}
```

---

#### PUT `/api/playas/{id}/configuracion`

Actualiza los parámetros de configuración de una playa.

**Autenticación:** Requerida (rol: administrador)

**Request Body:**

```json
{
  "area_por_visitante_m2": 20.00,
  "periodo_horas": 8,
  "tiempo_permanencia_horas": 4.0,
  "capacidad_manejo": 0.75
}
```

**Response 200:**

```json
{
  "playa_id": 1,
  "area_por_visitante_m2": 20.00,
  "periodo_horas": 8,
  "tiempo_permanencia_horas": 4.0,
  "capacidad_manejo": 0.75,
  "mensaje": "Configuración actualizada correctamente"
}
```

---

### 4.3 Registro de visitantes

#### POST `/api/visitantes/entrada`

Registra la entrada de visitantes a una playa.

**Autenticación:** Requerida

**Request Body:**

```json
{
  "playa_id": 1,
  "cantidad_personas": 3,
  "observaciones": "Grupo familiar"
}
```

**Response 201:**

```json
{
  "id": 45,
  "playa_id": 1,
  "playa_nombre": "Junquillal de la Cruz",
  "usuario_id": 1,
  "fecha_entrada": "2026-07-14T10:30:00",
  "fecha_salida": null,
  "cantidad_personas": 3,
  "observaciones": "Grupo familiar",
  "mensaje": "Entrada registrada correctamente"
}
```

---

#### PUT `/api/visitantes/{id}/salida`

Registra la salida de un visitante previamente registrado.

**Autenticación:** Requerida

**Parámetros de ruta:**

| Parámetro | Tipo | Descripción |
|---|---|---|
| id | int | ID del registro de visitante |

**Request Body (opcional):**

```json
{
  "fecha_salida": "2026-07-14T14:30:00"
}
```

**Response 200:**

```json
{
  "id": 45,
  "fecha_entrada": "2026-07-14T10:30:00",
  "fecha_salida": "2026-07-14T14:30:00",
  "cantidad_personas": 3,
  "mensaje": "Salida registrada correctamente"
}
```

---

#### GET `/api/visitantes/activos/{playa_id}`

Obtiene la cantidad de visitantes actualmente en una playa (sin fecha de salida).

**Autenticación:** Requerida

**Response 200:**

```json
{
  "playa_id": 1,
  "playa_nombre": "Junquillal de la Cruz",
  "total_visitantes": 87,
  "registros_activos": 32,
  "fecha_consulta": "2026-07-14T15:00:00"
}
```

---

#### GET `/api/visitantes/historial`

Obtiene el histórico de registros de visitantes con filtros opcionales.

**Autenticación:** Requerida

**Query parameters:**

| Parámetro | Tipo | Requerido | Descripción |
|---|---|---|---|
| playa_id | int | No | Filtrar por playa |
| fecha_inicio | date | No | Desde fecha |
| fecha_fin | date | No | Hasta fecha |
| page | int | No | Página (default: 1) |
| limit | int | No | Registros por página (default: 20) |

**Response 200:**

```json
{
  "total": 150,
  "page": 1,
  "limit": 20,
  "registros": [
    {
      "id": 45,
      "playa_id": 1,
      "playa_nombre": "Junquillal de la Cruz",
      "fecha_entrada": "2026-07-14T10:30:00",
      "fecha_salida": "2026-07-14T14:30:00",
      "cantidad_personas": 3
    }
  ]
}
```

---

### 4.4 Eventos ambientales

#### POST `/api/eventos`

Reporta un evento ambiental que afecta la capacidad de carga de una playa.

**Autenticación:** Requerida

**Request Body:**

```json
{
  "playa_id": 2,
  "tipo": "arribada_tortugas",
  "titulo": "Arribada de tortugas laúd",
  "descripcion": "Zona de anidación restringida en sector norte",
  "fecha_inicio": "2026-07-14T18:00:00",
  "parte_afectada": 8000.00,
  "totalidad_analizada": 32000.00
}
```

**Tipos de evento válidos:**

| Valor | Descripción |
|---|---|
| `arribada_tortugas` | Arribada o anidación de tortugas |
| `marea_roja` | Presencia de marea roja |
| `marea_alta` | Condición de marea alta |
| `condicion_climatica` | Clima adverso |
| `restriccion_acceso` | Restricción de acceso al sitio |
| `cierre_temporal` | Cierre temporal del área |
| `otro` | Otro evento ambiental |

**Response 201:**

```json
{
  "id": 12,
  "playa_id": 2,
  "tipo": "arribada_tortugas",
  "titulo": "Arribada de tortugas laúd",
  "factor_correccion": 0.7500,
  "activo": true,
  "mensaje": "Evento registrado. Factor de corrección = 0.75"
}
```

**Nota:** El factor de corrección se calcula automáticamente:

```
FC = 1 - (parte_afectada / totalidad_analizada)
FC = 1 - (8000 / 32000) = 0.75
```

---

#### GET `/api/eventos`

Lista todos los eventos ambientales registrados.

**Autenticación:** Requerida

**Query parameters:**

| Parámetro | Tipo | Requerido | Descripción |
|---|---|---|---|
| playa_id | int | No | Filtrar por playa |
| tipo | string | No | Filtrar por tipo |
| activo | boolean | No | Filtrar por estado |

**Response 200:**

```json
[
  {
    "id": 12,
    "playa_id": 2,
    "playa_nombre": "Playa Grande",
    "tipo": "arribada_tortugas",
    "titulo": "Arribada de tortugas laúd",
    "fecha_inicio": "2026-07-14T18:00:00",
    "fecha_fin": null,
    "factor_correccion": 0.7500,
    "activo": true
  }
]
```

---

#### GET `/api/eventos/activos/{playa_id}`

Lista los eventos ambientales activos de una playa.

**Autenticación:** Requerida

**Response 200:**

```json
{
  "playa_id": 1,
  "playa_nombre": "Junquillal de la Cruz",
  "total_eventos_activos": 1,
  "eventos": [
    {
      "id": 5,
      "tipo": "marea_alta",
      "titulo": "Marea alta matutina",
      "factor_correccion": 0.9000,
      "fecha_inicio": "2026-07-14T06:00:00"
    }
  ]
}
```

---

#### PUT `/api/eventos/{id}/cerrar`

Cierra un evento ambiental activo.

**Autenticación:** Requerida

**Request Body (opcional):**

```json
{
  "fecha_fin": "2026-07-14T20:00:00"
}
```

**Response 200:**

```json
{
  "id": 12,
  "activo": false,
  "fecha_fin": "2026-07-14T20:00:00",
  "mensaje": "Evento cerrado correctamente"
}
```

---

#### GET `/api/eventos/{id}/factores`

Obtiene los factores de corrección asociados a un evento.

**Autenticación:** Requerida

**Response 200:**

```json
{
  "evento_id": 12,
  "factores": [
    {
      "id": 1,
      "nombre_variable": "zona_anidacion",
      "valor": 0.7500
    }
  ]
}
```

---

### 4.5 Capacidad de carga (CCF, CCR, CCE)

#### GET `/api/capacidad/ccf/{playa_id}`

Calcula la Capacidad de Carga Física (CCF).

**Autenticación:** Requerida

**Fórmula:**

```
CCF = (area_util / area_por_visitante) × (periodo_horas / tiempo_permanencia_horas)
```

**Response 200:**

```json
{
  "playa_id": 1,
  "playa_nombre": "Junquillal de la Cruz",
  "ccf": 4500.00,
  "formula": "(45000 / 20) × (8 / 4) = 4500",
  "fecha_calculo": "2026-07-14T15:00:00"
}
```

---

#### GET `/api/capacidad/ccr/{playa_id}`

Calcula la Capacidad de Carga Real (CCR).

**Autenticación:** Requerida

**Fórmula:**

```
CCR = CCF × FC1 × FC2 × ... × FCn
FC = 1 - (parte_afectada / totalidad_analizada)
```

**Response 200:**

```json
{
  "playa_id": 1,
  "ccf": 4500.00,
  "factores_correccion": [0.9000],
  "ccr_formula": 4050.00,
  "ccr_ml": null,
  "ccr_final": 4050.00,
  "metodo_ccr": "formula",
  "fecha_calculo": "2026-07-14T15:00:00"
}
```

---

#### GET `/api/capacidad/cce/{playa_id}`

Calcula la Capacidad de Carga Efectiva (CCE).

**Autenticación:** Requerida

**Fórmula:**

```
CCE = CCR × capacidad_manejo
```

**Response 200:**

```json
{
  "playa_id": 1,
  "ccr": 4050.00,
  "capacidad_manejo": 0.75,
  "cce": 3037.50,
  "fecha_calculo": "2026-07-14T15:00:00"
}
```

---

#### GET `/api/capacidad/estimacion/{playa_id}`

Endpoint principal. Retorna la estimación completa de capacidad de carga con ocupación actual.

**Autenticación:** Requerida

**Response 200:**

```json
{
  "playa_id": 1,
  "playa_nombre": "Junquillal de la Cruz",
  "fecha_calculo": "2026-07-14T15:00:00",
  "capacidad": {
    "ccf": 4500.00,
    "ccr_formula": 4050.00,
    "ccr_ml": null,
    "ccr_final": 4050.00,
    "cce": 3037.50,
    "metodo_ccr": "formula"
  },
  "ocupacion": {
    "visitantes_actuales": 87,
    "porcentaje_ocupacion": 2.15,
    "estado": "normal"
  },
  "eventos_activos": 1
}
```

**Estados de ocupación:**

| Estado | Condición |
|---|---|
| `normal` | Ocupación < 70% |
| `advertencia` | Ocupación entre 70% y 90% |
| `critico` | Ocupación > 90% |

---

#### GET `/api/capacidad/historial/{playa_id}`

Obtiene el histórico de estimaciones de capacidad de carga.

**Autenticación:** Requerida

**Query parameters:**

| Parámetro | Tipo | Requerido | Descripción |
|---|---|---|---|
| fecha_inicio | date | No | Desde fecha |
| fecha_fin | date | No | Hasta fecha |
| limit | int | No | Cantidad de registros (default: 30) |

**Response 200:**

```json
{
  "playa_id": 1,
  "total": 30,
  "estimaciones": [
    {
      "id": 100,
      "fecha_calculo": "2026-07-14T15:00:00",
      "ccf": 4500.00,
      "ccr_final": 4050.00,
      "cce": 3037.50,
      "visitantes_actuales": 87,
      "porcentaje_ocupacion": 2.15
    }
  ]
}
```

---

#### POST `/api/capacidad/calcular/{playa_id}`

Fuerza un recálculo de capacidad y guarda el resultado en el histórico.

**Autenticación:** Requerida

**Response 201:**

```json
{
  "playa_id": 1,
  "estimacion_id": 101,
  "ccf": 4500.00,
  "ccr_final": 4050.00,
  "cce": 3037.50,
  "mensaje": "Estimación calculada y guardada correctamente"
}
```

---

### 4.6 Dashboard

#### GET `/api/dashboard/{playa_id}`

Retorna el resumen completo para el panel informativo de una playa.

**Autenticación:** Requerida

**Response 200:**

```json
{
  "playa": {
    "id": 1,
    "nombre": "Junquillal de la Cruz",
    "area_util_m2": 45000.00
  },
  "ocupacion": {
    "visitantes_actuales": 87,
    "porcentaje": 2.15,
    "estado": "normal"
  },
  "capacidad": {
    "ccf": 4500,
    "ccr": 4050,
    "cce": 3037,
    "metodo_ccr": "formula"
  },
  "eventos_activos": [
    {
      "id": 5,
      "tipo": "marea_alta",
      "titulo": "Marea alta matutina",
      "factor_correccion": 0.9000
    }
  ],
  "ultimas_estimaciones": [
    {
      "fecha": "2026-07-14T08:00:00",
      "porcentaje_ocupacion": 1.20
    },
    {
      "fecha": "2026-07-14T12:00:00",
      "porcentaje_ocupacion": 1.85
    },
    {
      "fecha": "2026-07-14T15:00:00",
      "porcentaje_ocupacion": 2.15
    }
  ]
}
```

---

#### GET `/api/dashboard`

Retorna el resumen general de todas las playas.

**Autenticación:** Requerida

**Response 200:**

```json
{
  "fecha_consulta": "2026-07-14T15:00:00",
  "total_playas": 2,
  "playas": [
    {
      "id": 1,
      "nombre": "Junquillal de la Cruz",
      "visitantes_actuales": 87,
      "porcentaje_ocupacion": 2.15,
      "estado": "normal",
      "eventos_activos": 1
    },
    {
      "id": 2,
      "nombre": "Playa Grande",
      "visitantes_actuales": 45,
      "porcentaje_ocupacion": 1.48,
      "estado": "normal",
      "eventos_activos": 0
    }
  ]
}
```

---

### 4.7 Notificaciones

#### GET `/api/notificaciones`

Lista las notificaciones del usuario autenticado.

**Autenticación:** Requerida

**Query parameters:**

| Parámetro | Tipo | Requerido | Descripción |
|---|---|---|---|
| leida | boolean | No | Filtrar por estado de lectura |

**Response 200:**

```json
[
  {
    "id": 1,
    "titulo": "Evento ambiental reportado",
    "mensaje": "Se reportó arribada de tortugas en Playa Grande",
    "playa_nombre": "Playa Grande",
    "leida": false,
    "created_at": "2026-07-14T18:05:00"
  }
]
```

---

#### PUT `/api/notificaciones/{id}/leida`

Marca una notificación como leída.

**Autenticación:** Requerida

**Response 200:**

```json
{
  "id": 1,
  "leida": true,
  "mensaje": "Notificación marcada como leída"
}
```

---

### 4.8 Machine Learning

#### GET `/api/ml/estado/{playa_id}`

Consulta si existe un modelo ML entrenado y activo para una playa.

**Autenticación:** Requerida

**Response 200:**

```json
{
  "playa_id": 1,
  "modelo_activo": false,
  "registros_disponibles": 12,
  "registros_minimos": 50,
  "ultimo_entrenamiento": null,
  "mensaje": "Datos insuficientes. Se utiliza CCR por fórmula."
}
```

---

#### POST `/api/ml/entrenar/{playa_id}`

Entrena el modelo DecisionTreeRegressor con los datos históricos disponibles.

**Autenticación:** Requerida (rol: administrador)

**Response 200:**

```json
{
  "playa_id": 1,
  "modelo_activo": true,
  "registros_usados": 80,
  "metricas": {
    "r2": 0.85,
    "mae": 120.50
  },
  "mensaje": "Modelo entrenado correctamente"
}
```

**Response 400 (datos insuficientes):**

```json
{
  "detail": "Datos insuficientes para entrenar. Se requieren al menos 50 registros."
}
```

---

#### GET `/api/ml/prediccion/{playa_id}`

Obtiene la predicción de CCR mediante el modelo ML.

**Autenticación:** Requerida

**Response 200:**

```json
{
  "playa_id": 1,
  "ccr_ml": 3920.00,
  "ccr_formula": 4050.00,
  "variables_usadas": {
    "visitantes_actuales": 87,
    "porcentaje_ocupacion": 2.15,
    "eventos_activos": 1
  },
  "modelo_activo": true,
  "fecha_prediccion": "2026-07-14T15:00:00"
}
```

**Response 404 (sin modelo):**

```json
{
  "detail": "No hay modelo ML activo para esta playa. Use CCR por fórmula."
}
```

---

## 5. Endpoints prioritarios para implementación (MVP)

Orden sugerido de desarrollo:

| Prioridad | Endpoint | Motivo |
|---|---|---|
| 1 | POST `/api/auth/login` | Autenticación base |
| 2 | GET `/api/playas` | Datos base del sistema |
| 3 | POST `/api/visitantes/entrada` | Funcionalidad core |
| 4 | PUT `/api/visitantes/{id}/salida` | Funcionalidad core |
| 5 | GET `/api/visitantes/activos/{playa_id}` | Ocupación en tiempo real |
| 6 | POST `/api/eventos` | Eventos ambientales |
| 7 | GET `/api/capacidad/estimacion/{playa_id}` | Cálculo CCF/CCR/CCE |
| 8 | GET `/api/dashboard/{playa_id}` | Panel principal |

---

## 6. Relación endpoint ↔ pantalla frontend

| Pantalla React | Endpoints que consume |
|---|---|
| Login | POST `/api/auth/login` |
| Dashboard | GET `/api/dashboard/{playa_id}` |
| Registro visitantes | POST `/api/visitantes/entrada`, PUT `/api/visitantes/{id}/salida` |
| Eventos ambientales | POST `/api/eventos`, GET `/api/eventos/activos/{playa_id}` |
| Reportes capacidad | GET `/api/capacidad/historial/{playa_id}` |
| Configuración (admin) | GET/PUT `/api/playas/{id}/configuracion` |
| ML (admin) | GET `/api/ml/estado/{playa_id}`, POST `/api/ml/entrenar/{playa_id}` |

---

## 7. Notas para implementación

1. Todos los endpoints protegidos validan el token JWT en el header `Authorization`.
2. Las fechas se almacenan en UTC y se retornan en ISO 8601.
3. El cálculo de CCR usa fórmula por defecto; ML es complementario.
4. Si no hay modelo ML activo, `ccr_final` = `ccr_formula`.
5. FastAPI generará documentación interactiva automática en `/docs` (Swagger UI).
6. Los errores de validación retornan código 422 con detalle de campos inválidos.

---

*Documento de diseño — Doc 08 · Sistema CEMEDE Capacidad de Carga Turística*
