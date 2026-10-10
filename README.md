# Cemede

Sistema web para la estimación de la capacidad de carga turística y su impacto ambiental en las playas Junquillal de la Cruz y Playa Grande, Guanacaste.

**Programa:** CEMEDE-UNA  
**Stack:** React · FastAPI · MySQL · scikit-learn

## Estructura del proyecto

```
Proyecto-CEMEDE/
├── backend/          # API FastAPI (Python)
├── database/         # Schema y datos semilla MySQL
├── docs/             # Documentación de diseño (Doc 08)
└── frontend/         # React (próximamente)
```

## Documentación de diseño (Doc 08)

- [Lista de endpoints REST](docs/lista-endpoints-rest.md)
- [Fórmulas CCF / CCR / CCE](docs/formulas-capacidad-carga.md)

## Base de datos MySQL

1. Asegúrate de tener MySQL corriendo.
2. Ejecuta el schema:

```bash
mysql -u root -p < database/schema.sql
```

3. Carga datos semilla:

```bash
mysql -u root -p < database/seed.sql
```

Si la base ya existía antes del módulo de notificaciones, aplica las migraciones:

```bash
mysql -u root -p < database/migration-add-notification-deduplication-key.sql
mysql -u root -p < database/migration-add-event-approval-workflow.sql
mysql -u root -p < database/migration-add-visita-duracion-estimada.sql
mysql -u root -p < database/migration-add-roles-permisos.sql
mysql -u root -p < database/migration-add-debe-cambiar-password.sql
mysql -u root -p < database/migration-add-visitacion-historica.sql
mysql -u root -p < database/migration-add-ml-modelo.sql
```

### Histórico de visitación (Excel) y estimaciones para ML

1. Configura `VISITACION_EXCEL_PATH` en `backend/.env` (ruta al xlsx 2000–2024).
2. Importa y genera filas en `estimacion_capacidad`:

```bash
cd backend
source .venv/bin/activate
python scripts/import_historico.py
```

O vía API (admin con permiso `ml.gestionar` / `capacidad.gestionar`):

- `POST /api/historico/importar-excel`
- `POST /api/historico/sincronizar-estimaciones`
- `POST /api/ml/entrenar/{playa_id}`

**Usuarios de prueba** (password: `cemede2026`):

| Email | Rol |
|---|---|
| admin@cemede.una.ac.cr | administrador |
| investigador@cemede.una.ac.cr | investigador |

## Backend FastAPI

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Edita .env con tu DATABASE_URL y SECRET_KEY
uvicorn app.main:app --reload --port 8000
```

- **Swagger UI:** http://localhost:8000/docs
- **Health check:** http://localhost:8000/health

## Endpoints MVP implementados

- `POST /api/auth/login`
- `GET /api/auth/me`
- `GET /api/playas`
- `POST /api/playas`
- `GET /api/playas/{id}`
- `DELETE /api/playas/{id}`
- `GET /api/playas/{id}/configuracion`
- `PUT /api/playas/{id}/configuracion`
- `POST /api/visitantes/entrada`
- `PUT /api/visitantes/{id}/salida`
- `GET /api/visitantes/activos/{playa_id}`
- `GET /api/visitantes/historial`
- `POST /api/eventos`
- `GET /api/eventos`
- `GET /api/eventos/pendientes`
- `GET /api/eventos/activos/{playa_id}`
- `PUT /api/eventos/{id}/aprobar`
- `PUT /api/eventos/{id}/rechazar`
- `PUT /api/eventos/{id}/cerrar`
- `GET /api/avisos/publicos`
- `GET /api/capacidad/estimacion/{playa_id}`
- `POST /api/capacidad/calcular/{playa_id}`
- `GET /api/capacidad/historial/{playa_id}`
- `GET /api/dashboard/{playa_id}`
- `GET /api/dashboard`
- `GET /api/notificaciones`
- `PUT /api/notificaciones/{id}/leida`
- `GET /api/capacidad/ccf/{playa_id}`
- `GET /api/capacidad/ccr/{playa_id}`
- `GET /api/capacidad/cce/{playa_id}`
- `POST /api/historico/importar-excel`
- `POST /api/historico/sincronizar-estimaciones`
- `GET /api/historico/visitacion`
- `GET /api/ml/estado/{playa_id}`
- `POST /api/ml/entrenar/{playa_id}`
- `GET /api/ml/prediccion/{playa_id}`
