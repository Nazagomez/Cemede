USE cemede_capacidad_carga;

CREATE TABLE IF NOT EXISTS visitacion_historica (
  id INT AUTO_INCREMENT PRIMARY KEY,
  playa_id INT NOT NULL,
  anio INT NOT NULL,
  tipo_visitante VARCHAR(80) NOT NULL,
  cantidad_visitas INT NOT NULL DEFAULT 0,
  calidad_dato VARCHAR(120) NULL,
  fuente TEXT NULL,
  url_fuente TEXT NULL,
  observacion TEXT NULL,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT fk_visitacion_historica_playa FOREIGN KEY (playa_id) REFERENCES playa(id),
  CONSTRAINT uq_visitacion_playa_anio_tipo UNIQUE (playa_id, anio, tipo_visitante)
) ENGINE=InnoDB;

ALTER TABLE estimacion_capacidad
  ADD COLUMN eventos_activos INT NOT NULL DEFAULT 0 AFTER porcentaje_ocupacion;
