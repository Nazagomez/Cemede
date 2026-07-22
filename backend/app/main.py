"""FastAPI application entry point."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routers import auth, playas, visitantes

app = FastAPI(
    title="CEMEDE - Capacidad de Carga Turística",
    description="API para estimación de capacidad de carga en playas Junquillal y Playa Grande",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.get_cors_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix=settings.api_prefix)
app.include_router(playas.router, prefix=settings.api_prefix)
app.include_router(visitantes.router, prefix=settings.api_prefix)


@app.get("/health")
def health_check() -> dict[str, str]:
    """Health check endpoint."""
    return {"status": "ok", "service": "cemede-api"}
