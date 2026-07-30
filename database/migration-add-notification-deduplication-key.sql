-- Add concurrency-safe occupancy notification deduplication.
USE cemede_capacidad_carga;

ALTER TABLE notificacion
  ADD COLUMN deduplication_key VARCHAR(255) NULL AFTER leida,
  ADD CONSTRAINT uq_notificacion_deduplication_key UNIQUE (deduplication_key);
