-- =============================================
-- CEMEDE - Datos semilla
-- Password por defecto: cemede2026
-- =============================================

USE cemede_capacidad_carga;

-- Limpiar datos (solo desarrollo)
SET FOREIGN_KEY_CHECKS = 0;
TRUNCATE TABLE notificacion;
TRUNCATE TABLE estimacion_capacidad;
TRUNCATE TABLE factor_correccion;
TRUNCATE TABLE evento_ambiental;
TRUNCATE TABLE registro_visitante;
TRUNCATE TABLE configuracion_ccf;
TRUNCATE TABLE playa;
TRUNCATE TABLE usuario;
SET FOREIGN_KEY_CHECKS = 1;

INSERT INTO usuario (nombre, email, password_hash, rol) VALUES
(
  'Administrador CEMEDE',
  'admin@cemede.una.ac.cr',
  '$2b$12$nIbUGsxK2nVel/HgBjrO2.K1qYkweXMEsRfmAktAPg/Tt8CKPIXjO',
  'administrador'
),
(
  'Investigador CEMEDE',
  'investigador@cemede.una.ac.cr',
  '$2b$12$nIbUGsxK2nVel/HgBjrO2.K1qYkweXMEsRfmAktAPg/Tt8CKPIXjO',
  'investigador'
);

INSERT INTO playa (nombre, descripcion, area_util_m2, canton, provincia, latitud, longitud) VALUES
(
  'Junquillal de la Cruz',
  'Refugio Nacional de Vida Silvestre Bahía Junquillal',
  45000.00,
  'La Cruz',
  'Guanacaste',
  11.0300000,
  -85.7200000
),
(
  'Playa Grande',
  'Parque Nacional Marino Las Baulas',
  32000.00,
  'Santa Cruz',
  'Guanacaste',
  10.3400000,
  -85.8400000
);

INSERT INTO configuracion_ccf (playa_id, area_por_visitante_m2, periodo_horas, tiempo_permanencia_horas, capacidad_manejo) VALUES
(1, 20.00, 8, 4.00, 0.7532),
(2, 15.00, 8, 3.50, 0.8000);

-- Evento de ejemplo: marea alta en Junquillal (FC = 1 - 5000/45000 = 0.8889)
INSERT INTO evento_ambiental (
  playa_id, usuario_id, tipo, titulo, descripcion,
  fecha_inicio, parte_afectada, totalidad_analizada, activo
) VALUES (
  1, 2, 'marea_alta', 'Marea alta sector sur',
  'Sector sur parcialmente inundado durante la mañana',
  NOW(), 5000.00, 45000.00, TRUE
);

INSERT INTO factor_correccion (evento_id, nombre_variable, valor) VALUES
(1, 'marea_alta', 0.8889);

-- Registros de visitantes de ejemplo (activos)
INSERT INTO registro_visitante (playa_id, usuario_id, fecha_entrada, cantidad_personas) VALUES
(1, 2, DATE_SUB(NOW(), INTERVAL 2 HOUR), 3),
(1, 2, DATE_SUB(NOW(), INTERVAL 1 HOUR), 2),
(2, 2, DATE_SUB(NOW(), INTERVAL 3 HOUR), 5);
