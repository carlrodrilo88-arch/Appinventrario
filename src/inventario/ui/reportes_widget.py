from __future__ import annotations

from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QTabWidget,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from inventario.config import REPORTES_PDF_DIR
from inventario.modules.reportes.service import ReporteService
from inventario.utils import open_file


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

        export_stock_button = QPushButton("Exportar stock actual a PDF")
        export_stock_button.clicked.connect(self._export_stock_actual)
        open_stock_button = QPushButton("Abrir stock actual PDF")
        open_stock_button.clicked.connect(lambda: self._abrir_pdf("stock_actual.pdf"))
        export_bajo_button = QPushButton("Exportar stock bajo a PDF")
        export_bajo_button.clicked.connect(self._export_stock_bajo)
        open_bajo_button = QPushButton("Abrir stock bajo PDF")
        open_bajo_button.clicked.connect(lambda: self._abrir_pdf("stock_bajo.pdf"))
        export_mov_button = QPushButton("Exportar movimientos a PDF")
        export_mov_button.clicked.connect(self._export_movimientos)
        open_mov_button = QPushButton("Abrir movimientos PDF")
        open_mov_button.clicked.connect(lambda: self._abrir_pdf("movimientos_generales.pdf"))

        self.tabs.addTab(self._wrap_table(self.stock_actual_table), "Stock actual")
        self.tabs.addTab(self._wrap_table(self.stock_bajo_table), "Stock bajo")
        self.tabs.addTab(self._wrap_table(self.movimientos_table), "Movimientos")

        buttons_layout = QHBoxLayout()
        buttons_layout.addWidget(refresh_button)
        buttons_layout.addWidget(export_stock_button)
        buttons_layout.addWidget(open_stock_button)
        buttons_layout.addWidget(export_bajo_button)
        buttons_layout.addWidget(open_bajo_button)
        buttons_layout.addWidget(export_mov_button)
        buttons_layout.addWidget(open_mov_button)

        layout = QVBoxLayout()
        layout.addWidget(QLabel("Reportes"))
        layout.addLayout(buttons_layout)
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

    def _export_stock_actual(self) -> None:
        pdf_path = self.reporte_service.exportar_stock_actual_pdf()
        QMessageBox.information(self, "Reportes", f"PDF generado en:\n{pdf_path}")

    def _export_stock_bajo(self) -> None:
        pdf_path = self.reporte_service.exportar_stock_bajo_pdf()
        QMessageBox.information(self, "Reportes", f"PDF generado en:\n{pdf_path}")

    def _export_movimientos(self) -> None:
        pdf_path = self.reporte_service.exportar_movimientos_pdf()
        QMessageBox.information(self, "Reportes", f"PDF generado en:\n{pdf_path}")

    def _abrir_pdf(self, file_name: str) -> None:
        pdf_path = REPORTES_PDF_DIR / file_name
        try:
            open_file(pdf_path)
        except FileNotFoundError as exc:
            QMessageBox.warning(self, "Reportes", str(exc))
        except OSError as exc:
            QMessageBox.warning(self, "Reportes", f"No se pudo abrir el PDF: {exc}")
