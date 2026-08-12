-- Migration: event approval workflow and public announcements
USE cemede_capacidad_carga;

ALTER TABLE evento_ambiental
  MODIFY usuario_id INT NULL,
  MODIFY activo BOOLEAN NOT NULL DEFAULT FALSE,
  ADD COLUMN estado ENUM('pendiente', 'aprobado', 'rechazado', 'cerrado') NOT NULL DEFAULT 'pendiente' AFTER activo,
  ADD COLUMN origen ENUM('visitante', 'investigador', 'administrador') NOT NULL DEFAULT 'visitante' AFTER estado,
  ADD COLUMN reportado_por VARCHAR(150) NULL AFTER origen,
  ADD COLUMN aprobado_por INT NULL AFTER reportado_por,
  ADD COLUMN fecha_aprobacion DATETIME NULL AFTER aprobado_por,
  ADD CONSTRAINT fk_evento_aprobado_por FOREIGN KEY (aprobado_por) REFERENCES usuario(id);

UPDATE evento_ambiental
SET estado = 'aprobado'
WHERE activo = TRUE;

UPDATE evento_ambiental
SET estado = 'cerrado'
WHERE activo = FALSE AND fecha_fin IS NOT NULL;

CREATE TABLE IF NOT EXISTS aviso_publico (
  id INT AUTO_INCREMENT PRIMARY KEY,
  evento_id INT NULL,
  playa_id INT NOT NULL,
  tipo ENUM('evento_pendiente', 'evento_aprobado', 'evento_cerrado') NOT NULL,
  titulo VARCHAR(200) NOT NULL,
  mensaje TEXT NOT NULL,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT fk_aviso_evento FOREIGN KEY (evento_id) REFERENCES evento_ambiental(id),
  CONSTRAINT fk_aviso_playa FOREIGN KEY (playa_id) REFERENCES playa(id)
) ENGINE=InnoDB;
