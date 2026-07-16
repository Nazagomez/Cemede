# Cemede

Sistema web para la estimación de la capacidad de carga turística y su impacto ambiental en las playas Junquillal de la Cruz y Playa Grande, Guanacaste.

**Programa:** CEMEDE-UNA  
**Stack:** React · FastAPI · MySQL · scikit-learn

## Documentación de diseño (Doc 08)

- [Lista de endpoints REST](docs/lista-endpoints-rest.md)
- [Fórmulas CCF / CCR / CCE](docs/formulas-capacidad-carga.md)

## Fase 1 — Setup

### Base de datos MySQL

```bash
mysql -u root -p < database/schema.sql
mysql -u root -p < database/seed.sql
```

### Backend FastAPI

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload --port 8000
```

- **Swagger:** http://localhost:8000/docs
- **Health:** http://localhost:8000/health
