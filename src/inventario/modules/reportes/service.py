from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy import text
from sqlalchemy.orm import Session


@dataclass(slots=True)
class StockActualRecord:
    codigo: str
    nombre: str
    unidad_medida: str
    stock_actual: int
    stock_minimo: int
    activo: int
    ultima_actualizacion: str


@dataclass(slots=True)
class StockBajoRecord:
    codigo: str
    nombre: str
    stock_actual: int
    stock_minimo: int
    diferencia_faltante: int
    ultima_actualizacion: str


@dataclass(slots=True)
class MovimientoGeneralRecord:
    codigo_producto: str
    nombre_producto: str
    tipo_movimiento: str
    tipo: str
    cantidad: int
    fecha: str
    usuario: str
    observacion: str
    ultima_actualizacion: str


class ReporteService:
    def __init__(self, session: Session) -> None:
        self.session = session

    def obtener_stock_actual(self) -> list[StockActualRecord]:
        sql = """
        SELECT
            codigo,
            nombre,
            unidad_medida,
            stock_actual,
            stock_minimo,
            activo,
            ultima_actualizacion
        FROM reporte_stock_actual
        ORDER BY nombre ASC
        """
        rows = self.session.execute(text(sql)).mappings()
        return [StockActualRecord(**row) for row in rows]

    def obtener_stock_bajo(self) -> list[StockBajoRecord]:
        sql = """
        SELECT
            codigo,
            nombre,
            stock_actual,
            stock_minimo,
            diferencia_faltante,
            ultima_actualizacion
        FROM reporte_productos_stock_bajo
        ORDER BY diferencia_faltante DESC, nombre ASC
        """
        rows = self.session.execute(text(sql)).mappings()
        return [StockBajoRecord(**row) for row in rows]

    def obtener_movimientos_generales(self) -> list[MovimientoGeneralRecord]:
        sql = """
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
        FROM reporte_movimientos_generales
        ORDER BY fecha DESC
        """
        rows = self.session.execute(text(sql)).mappings()
        return [MovimientoGeneralRecord(**row) for row in rows]
