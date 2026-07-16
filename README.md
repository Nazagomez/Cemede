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
- `GET /api/playas/{id}`
- `GET /api/playas/{id}/configuracion`
- `POST /api/visitantes/entrada`
- `PUT /api/visitantes/{id}/salida`
- `GET /api/visitantes/activos/{playa_id}`
- `POST /api/eventos`
- `GET /api/eventos/activos/{playa_id}`
- `GET /api/capacidad/estimacion/{playa_id}`
- `GET /api/dashboard/{playa_id}`
