-- =============================================
-- CEMEDE - Capacidad de Carga Turística
-- Schema MySQL
-- =============================================

CREATE DATABASE IF NOT EXISTS cemede_capacidad_carga
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE cemede_capacidad_carga;

-- --- ENUM-like via ENUM columns ---

CREATE TABLE IF NOT EXISTS usuario (
  id INT AUTO_INCREMENT PRIMARY KEY,
  nombre VARCHAR(100) NOT NULL,
  email VARCHAR(150) NOT NULL UNIQUE,
  password_hash VARCHAR(255) NOT NULL,
  rol ENUM('investigador', 'administrador') NOT NULL DEFAULT 'investigador',
  activo BOOLEAN NOT NULL DEFAULT TRUE,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS playa (
  id INT AUTO_INCREMENT PRIMARY KEY,
  nombre VARCHAR(150) NOT NULL,
  descripcion TEXT,
  area_util_m2 DECIMAL(12, 2) NOT NULL,
  canton VARCHAR(100) NOT NULL,
  provincia VARCHAR(100) NOT NULL DEFAULT 'Guanacaste',
  latitud DECIMAL(10, 7),
  longitud DECIMAL(10, 7),
  activa BOOLEAN NOT NULL DEFAULT TRUE,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS configuracion_ccf (
  id INT AUTO_INCREMENT PRIMARY KEY,
  playa_id INT NOT NULL UNIQUE,
  area_por_visitante_m2 DECIMAL(8, 2) NOT NULL,
  periodo_horas INT NOT NULL DEFAULT 8,
  tiempo_permanencia_horas DECIMAL(5, 2) NOT NULL,
  capacidad_manejo DECIMAL(4, 2) NOT NULL DEFAULT 0.75,
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  CONSTRAINT fk_config_playa FOREIGN KEY (playa_id) REFERENCES playa(id)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS registro_visitante (
  id INT AUTO_INCREMENT PRIMARY KEY,
  playa_id INT NOT NULL,
  usuario_id INT NOT NULL,
  fecha_entrada DATETIME NOT NULL,
  fecha_salida DATETIME NULL,
  cantidad_personas INT NOT NULL DEFAULT 1,
  observaciones TEXT,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT fk_visitante_playa FOREIGN KEY (playa_id) REFERENCES playa(id),
  CONSTRAINT fk_visitante_usuario FOREIGN KEY (usuario_id) REFERENCES usuario(id)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS evento_ambiental (
  id INT AUTO_INCREMENT PRIMARY KEY,
  playa_id INT NOT NULL,
  usuario_id INT NOT NULL,
  tipo ENUM(
    'arribada_tortugas',
    'marea_roja',
    'marea_alta',
    'condicion_climatica',
    'restriccion_acceso',
    'cierre_temporal',
    'otro'
  ) NOT NULL,
  titulo VARCHAR(200) NOT NULL,
  descripcion TEXT,
  fecha_inicio DATETIME NOT NULL,
  fecha_fin DATETIME NULL,
  parte_afectada DECIMAL(10, 2) NOT NULL,
  totalidad_analizada DECIMAL(10, 2) NOT NULL,
  activo BOOLEAN NOT NULL DEFAULT TRUE,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT fk_evento_playa FOREIGN KEY (playa_id) REFERENCES playa(id),
  CONSTRAINT fk_evento_usuario FOREIGN KEY (usuario_id) REFERENCES usuario(id)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS factor_correccion (
  id INT AUTO_INCREMENT PRIMARY KEY,
  evento_id INT NOT NULL,
  nombre_variable VARCHAR(100) NOT NULL,
  valor DECIMAL(6, 4) NOT NULL,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT fk_factor_evento FOREIGN KEY (evento_id) REFERENCES evento_ambiental(id)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS estimacion_capacidad (
  id INT AUTO_INCREMENT PRIMARY KEY,
  playa_id INT NOT NULL,
  fecha_calculo DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  ccf DECIMAL(10, 2) NOT NULL,
  ccr_formula DECIMAL(10, 2),
  ccr_ml DECIMAL(10, 2),
  ccr_final DECIMAL(10, 2) NOT NULL,
  cce DECIMAL(10, 2) NOT NULL,
  visitantes_actuales INT NOT NULL DEFAULT 0,
  porcentaje_ocupacion DECIMAL(6, 2) NOT NULL DEFAULT 0,
  metodo_ccr ENUM('formula', 'machine_learning', 'hibrido') NOT NULL DEFAULT 'formula',
  CONSTRAINT fk_estimacion_playa FOREIGN KEY (playa_id) REFERENCES playa(id)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS notificacion (
  id INT AUTO_INCREMENT PRIMARY KEY,
  usuario_id INT NOT NULL,
  evento_id INT NULL,
  playa_id INT NOT NULL,
  titulo VARCHAR(200) NOT NULL,
  mensaje TEXT NOT NULL,
  leida BOOLEAN NOT NULL DEFAULT FALSE,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT fk_notificacion_usuario FOREIGN KEY (usuario_id) REFERENCES usuario(id),
  CONSTRAINT fk_notificacion_evento FOREIGN KEY (evento_id) REFERENCES evento_ambiental(id),
  CONSTRAINT fk_notificacion_playa FOREIGN KEY (playa_id) REFERENCES playa(id)
) ENGINE=InnoDB;

CREATE INDEX idx_registro_playa_activo ON registro_visitante (playa_id, fecha_salida);
CREATE INDEX idx_evento_playa_activo ON evento_ambiental (playa_id, activo);
CREATE INDEX idx_estimacion_playa_fecha ON estimacion_capacidad (playa_id, fecha_calculo);
