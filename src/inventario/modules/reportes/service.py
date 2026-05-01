from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from sqlalchemy import text
from sqlalchemy.orm import Session

from inventario.reports.pdf import generar_pdf_tabular


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
    def __init__(self, session: Session, output_dir: Path) -> None:
        self.session = session
        self.output_dir = output_dir

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

    def exportar_stock_actual_pdf(self) -> Path:
        registros = self.obtener_stock_actual()
        filas = [
            [
                r.codigo,
                r.nombre,
                r.unidad_medida,
                str(r.stock_actual),
                str(r.stock_minimo),
                "Si" if r.activo else "No",
                r.ultima_actualizacion,
            ]
            for r in registros
        ]
        return generar_pdf_tabular(
            "Reporte de stock actual",
            ["Codigo", "Nombre", "Unidad", "Stock", "Minimo", "Activo", "Actualizacion"],
            filas,
            self.output_dir / "stock_actual.pdf",
        )

    def exportar_stock_bajo_pdf(self) -> Path:
        registros = self.obtener_stock_bajo()
        filas = [
            [
                r.codigo,
                r.nombre,
                str(r.stock_actual),
                str(r.stock_minimo),
                str(r.diferencia_faltante),
                r.ultima_actualizacion,
            ]
            for r in registros
        ]
        return generar_pdf_tabular(
            "Reporte de productos con stock bajo",
            ["Codigo", "Nombre", "Stock", "Minimo", "Faltante", "Actualizacion"],
            filas,
            self.output_dir / "stock_bajo.pdf",
        )

    def exportar_movimientos_pdf(self) -> Path:
        registros = self.obtener_movimientos_generales()
        filas = [
            [
                r.codigo_producto,
                r.nombre_producto,
                r.tipo_movimiento,
                r.tipo,
                str(r.cantidad),
                r.fecha,
                r.usuario,
                r.observacion or "-",
            ]
            for r in registros
        ]
        return generar_pdf_tabular(
            "Reporte de movimientos generales",
            ["Codigo", "Nombre", "Movimiento", "Tipo", "Cantidad", "Fecha", "Usuario", "Obs"],
            filas,
            self.output_dir / "movimientos_generales.pdf",
        )
