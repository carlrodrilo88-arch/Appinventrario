from __future__ import annotations

from PySide6.QtWidgets import (
    QLabel,
    QPushButton,
    QTabWidget,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from inventario.modules.reportes.service import ReporteService


class ReportesWidget(QWidget):
    def __init__(self, reporte_service: ReporteService) -> None:
        super().__init__()
        self.reporte_service = reporte_service

        self.tabs = QTabWidget()
        self.stock_actual_table = QTableWidget(0, 7)
        self.stock_bajo_table = QTableWidget(0, 6)
        self.movimientos_table = QTableWidget(0, 8)

        self.stock_actual_table.setHorizontalHeaderLabels(
            [
                "Codigo",
                "Nombre",
                "Unidad",
                "Stock actual",
                "Stock minimo",
                "Activo",
                "Ultima actualizacion",
            ]
        )
        self.stock_bajo_table.setHorizontalHeaderLabels(
            [
                "Codigo",
                "Nombre",
                "Stock actual",
                "Stock minimo",
                "Diferencia faltante",
                "Ultima actualizacion",
            ]
        )
        self.movimientos_table.setHorizontalHeaderLabels(
            [
                "Codigo",
                "Nombre",
                "Movimiento",
                "Tipo",
                "Cantidad",
                "Fecha",
                "Usuario",
                "Observacion",
            ]
        )

        self._build_ui()
        self._load_reportes()

    def _build_ui(self) -> None:
        refresh_button = QPushButton("Actualizar reportes")
        refresh_button.clicked.connect(self._load_reportes)

        self.tabs.addTab(self._wrap_table(self.stock_actual_table), "Stock actual")
        self.tabs.addTab(self._wrap_table(self.stock_bajo_table), "Stock bajo")
        self.tabs.addTab(self._wrap_table(self.movimientos_table), "Movimientos")

        layout = QVBoxLayout()
        layout.addWidget(QLabel("Reportes"))
        layout.addWidget(refresh_button)
        layout.addWidget(self.tabs)
        self.setLayout(layout)

    def _wrap_table(self, table: QTableWidget) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout()
        layout.addWidget(table)
        widget.setLayout(layout)
        return widget

    def _load_reportes(self) -> None:
        self._load_stock_actual()
        self._load_stock_bajo()
        self._load_movimientos()

    def _load_stock_actual(self) -> None:
        records = self.reporte_service.obtener_stock_actual()
        self.stock_actual_table.setRowCount(len(records))

        for row, record in enumerate(records):
            values = [
                record.codigo,
                record.nombre,
                record.unidad_medida,
                str(record.stock_actual),
                str(record.stock_minimo),
                "Si" if record.activo else "No",
                record.ultima_actualizacion,
            ]
            for column, value in enumerate(values):
                self.stock_actual_table.setItem(row, column, QTableWidgetItem(value))

        self.stock_actual_table.resizeColumnsToContents()

    def _load_stock_bajo(self) -> None:
        records = self.reporte_service.obtener_stock_bajo()
        self.stock_bajo_table.setRowCount(len(records))

        for row, record in enumerate(records):
            values = [
                record.codigo,
                record.nombre,
                str(record.stock_actual),
                str(record.stock_minimo),
                str(record.diferencia_faltante),
                record.ultima_actualizacion,
            ]
            for column, value in enumerate(values):
                self.stock_bajo_table.setItem(row, column, QTableWidgetItem(value))

        self.stock_bajo_table.resizeColumnsToContents()

    def _load_movimientos(self) -> None:
        records = self.reporte_service.obtener_movimientos_generales()
        self.movimientos_table.setRowCount(len(records))

        for row, record in enumerate(records):
            values = [
                record.codigo_producto,
                record.nombre_producto,
                record.tipo_movimiento,
                record.tipo,
                str(record.cantidad),
                record.fecha,
                record.usuario,
                record.observacion,
            ]
            for column, value in enumerate(values):
                self.movimientos_table.setItem(row, column, QTableWidgetItem(value))

        self.movimientos_table.resizeColumnsToContents()
