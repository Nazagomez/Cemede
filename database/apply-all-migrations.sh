#!/usr/bin/env bash
# Apply all incremental migrations in order (existing DB, not fresh schema).
set -euo pipefail
DB="${1:-cemede_capacidad_carga}"
DIR="$(cd "$(dirname "$0")" && pwd)"
for file in \
  migration-add-notification-deduplication-key.sql \
  migration-add-event-approval-workflow.sql \
  migration-add-visita-duracion-estimada.sql \
  migration-add-roles-permisos.sql \
  migration-add-debe-cambiar-password.sql \
  migration-add-visitacion-historica.sql \
  migration-add-ml-modelo.sql
do
  echo "Applying $file ..."
  mysql -u root -p "$DB" < "$DIR/$file"
done
echo "Done."
