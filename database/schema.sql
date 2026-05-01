PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS productos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    codigo TEXT NOT NULL UNIQUE,
    nombre TEXT NOT NULL,
    unidad_medida TEXT NOT NULL,
    stock_actual INTEGER NOT NULL DEFAULT 0 CHECK (stock_actual >= 0),
    stock_minimo INTEGER NOT NULL DEFAULT 0 CHECK (stock_minimo >= 0),
    activo INTEGER NOT NULL DEFAULT 1 CHECK (activo IN (0, 1)),
    ultima_actualizacion TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS usuarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL,
    usuario TEXT NOT NULL UNIQUE,
    contrasena_hash TEXT NOT NULL,
    activo INTEGER NOT NULL DEFAULT 1 CHECK (activo IN (0, 1)),
    ultima_actualizacion TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS entradas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    producto_id INTEGER NOT NULL,
    cantidad INTEGER NOT NULL CHECK (cantidad > 0),
    fecha TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    tipo_entrada TEXT NOT NULL,
    observacion TEXT DEFAULT '',
    usuario_id INTEGER NOT NULL,
    ultima_actualizacion TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (producto_id) REFERENCES productos(id),
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
);

CREATE TABLE IF NOT EXISTS salidas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    producto_id INTEGER NOT NULL,
    cantidad INTEGER NOT NULL CHECK (cantidad > 0),
    fecha TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    tipo_salida TEXT NOT NULL,
    observacion TEXT DEFAULT '',
    usuario_id INTEGER NOT NULL,
    ultima_actualizacion TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (producto_id) REFERENCES productos(id),
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
);

CREATE INDEX IF NOT EXISTS idx_productos_codigo ON productos(codigo);
CREATE INDEX IF NOT EXISTS idx_productos_nombre ON productos(nombre);
CREATE INDEX IF NOT EXISTS idx_entradas_producto_fecha ON entradas(producto_id, fecha);
CREATE INDEX IF NOT EXISTS idx_salidas_producto_fecha ON salidas(producto_id, fecha);

CREATE TRIGGER IF NOT EXISTS trg_entradas_sumar_stock
AFTER INSERT ON entradas
FOR EACH ROW
BEGIN
    UPDATE productos
    SET stock_actual = stock_actual + NEW.cantidad,
        ultima_actualizacion = CURRENT_TIMESTAMP
    WHERE id = NEW.producto_id;
END;

CREATE TRIGGER IF NOT EXISTS trg_salidas_validar_stock
BEFORE INSERT ON salidas
FOR EACH ROW
BEGIN
    SELECT
        CASE
            WHEN (SELECT stock_actual FROM productos WHERE id = NEW.producto_id) < NEW.cantidad
            THEN RAISE(ABORT, 'Stock insuficiente para registrar la salida')
        END;
END;

CREATE TRIGGER IF NOT EXISTS trg_salidas_restar_stock
AFTER INSERT ON salidas
FOR EACH ROW
BEGIN
    UPDATE productos
    SET stock_actual = stock_actual - NEW.cantidad,
        ultima_actualizacion = CURRENT_TIMESTAMP
    WHERE id = NEW.producto_id;
END;

CREATE VIEW IF NOT EXISTS movimientos AS
SELECT
    e.id AS id,
    p.id AS producto_id,
    p.codigo AS codigo_producto,
    p.nombre AS nombre_producto,
    'entrada' AS tipo_movimiento,
    e.tipo_entrada AS tipo,
    e.cantidad AS cantidad,
    e.fecha AS fecha,
    u.usuario AS usuario,
    e.observacion AS observacion,
    NULL AS stock_resultante,
    e.ultima_actualizacion AS ultima_actualizacion
FROM entradas e
JOIN productos p ON p.id = e.producto_id
JOIN usuarios u ON u.id = e.usuario_id
UNION ALL
SELECT
    s.id AS id,
    p.id AS producto_id,
    p.codigo AS codigo_producto,
    p.nombre AS nombre_producto,
    'salida' AS tipo_movimiento,
    s.tipo_salida AS tipo,
    s.cantidad AS cantidad,
    s.fecha AS fecha,
    u.usuario AS usuario,
    s.observacion AS observacion,
    NULL AS stock_resultante,
    s.ultima_actualizacion AS ultima_actualizacion
FROM salidas s
JOIN productos p ON p.id = s.producto_id
JOIN usuarios u ON u.id = s.usuario_id;

CREATE VIEW IF NOT EXISTS reporte_stock_actual AS
SELECT
    codigo,
    nombre,
    unidad_medida,
    stock_actual,
    stock_minimo,
    activo,
    ultima_actualizacion
FROM productos;

CREATE VIEW IF NOT EXISTS reporte_productos_stock_bajo AS
SELECT
    codigo,
    nombre,
    stock_actual,
    stock_minimo,
    (stock_minimo - stock_actual) AS diferencia_faltante,
    ultima_actualizacion
FROM productos
WHERE activo = 1
  AND stock_actual <= stock_minimo;

CREATE VIEW IF NOT EXISTS reporte_movimientos_generales AS
SELECT
    codigo_producto,
    nombre_producto,
    tipo_movimiento,
    tipo,
    cantidad,
    fecha,
    usuario,
    observacion,
    ultima_actualizacion
FROM movimientos;
