USE cemede_capacidad_carga;

CREATE TABLE IF NOT EXISTS ml_modelo (
  playa_id INT NOT NULL PRIMARY KEY,
  activo BOOLEAN NOT NULL DEFAULT FALSE,
  registros_usados INT NOT NULL DEFAULT 0,
  mae DECIMAL(10, 2) NULL,
  rmse DECIMAL(10, 2) NULL,
  max_depth INT NOT NULL DEFAULT 4,
  min_samples_split INT NOT NULL DEFAULT 5,
  min_samples_leaf INT NOT NULL DEFAULT 2,
  random_state INT NOT NULL DEFAULT 42,
  ultimo_entrenamiento DATETIME NULL,
  CONSTRAINT fk_ml_modelo_playa FOREIGN KEY (playa_id) REFERENCES playa(id)
) ENGINE=InnoDB;
