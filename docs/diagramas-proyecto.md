# Diagramas del proyecto CEMEDE

Documento de referencia (Doc 08). Ver también `formulas-capacidad-carga.md` y `lista-endpoints-rest.md`.

## Arquitectura

- Frontend React (Frontend-CEMEDE) → API FastAPI → MySQL
- ML: scikit-learn DecisionTreeRegressor, artefactos en `backend/ml_artifacts/`

## Flujos principales

1. Visitantes: entrada/salida → ocupación → dashboard
2. Eventos: reporte → aprobación → factor corrección → CCR
3. Capacidad: CCF → CCR (fórmula ± ML) → CCE
4. Histórico: Excel visitación → `visitacion_historica` → `estimacion_capacidad` → entrenamiento ML
