USE cemede_capacidad_carga;

ALTER TABLE usuario
  MODIFY COLUMN rol ENUM('investigador','administrador','asistente') NOT NULL DEFAULT 'investigador';

ALTER TABLE evento_ambiental
  MODIFY COLUMN origen ENUM('visitante','investigador','administrador','asistente') NOT NULL DEFAULT 'visitante';

CREATE TABLE IF NOT EXISTS permiso (
  id INT AUTO_INCREMENT PRIMARY KEY,
  clave VARCHAR(100) NOT NULL UNIQUE,
  nombre VARCHAR(150) NOT NULL,
  descripcion VARCHAR(255) NULL
);

CREATE TABLE IF NOT EXISTS rol_permiso (
  rol ENUM('investigador','administrador','asistente') NOT NULL,
  permiso_id INT NOT NULL,
  PRIMARY KEY (rol, permiso_id),
  FOREIGN KEY (permiso_id) REFERENCES permiso(id) ON DELETE CASCADE
);

INSERT INTO permiso (clave, nombre, descripcion) VALUES
  ('playas.gestionar', 'Gestionar playas', 'Crear, editar y dar de baja playas monitoreadas.'),
  ('capacidad.gestionar', 'Recalcular capacidad de carga', 'Ejecutar y guardar un nuevo cálculo de capacidad.'),
  ('usuarios.gestionar', 'Administrar usuarios y roles', 'Crear usuarios, cambiar roles y configurar permisos.'),
  ('ml.gestionar', 'Gestionar modelo de predicción', 'Entrenar y administrar el modelo de Machine Learning.');

-- Administrador siempre tiene todos los permisos (protegido, no editable desde la UI)
INSERT INTO rol_permiso (rol, permiso_id)
SELECT 'administrador', id FROM permiso;

-- Investigador y Asistente arrancan sin permisos especiales — se asignan desde /admin/usuarios