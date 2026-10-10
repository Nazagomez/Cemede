"""CLI: import visitation Excel and sync historical estimacion_capacidad rows."""

import sys
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_ROOT))

from app.config import settings
from app.database import SessionLocal
from app.services.historico_service import (
    generate_estimaciones_from_visitacion,
    import_visitacion_from_excel,
    sync_config_from_field_params,
)


def main() -> None:
    """Run historical data import pipeline."""
    db = SessionLocal()
    try:
        import_result = import_visitacion_from_excel(db, settings.visitacion_excel_path)
        configs = sync_config_from_field_params(db)
        sync_result = generate_estimaciones_from_visitacion(db)
        db.commit()
        print("Importación:", import_result)
        print("Configuraciones CCF actualizadas:", configs)
        print("Estimaciones:", sync_result)
    finally:
        db.close()


if __name__ == "__main__":
    main()
