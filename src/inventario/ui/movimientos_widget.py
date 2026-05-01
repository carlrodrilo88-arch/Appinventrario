from __future__ import annotations

from PySide6.QtWidgets import (
    QComboBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from inventario.modules.movimientos.service import MovimientoService


class MovimientosWidget(QWidget):
    def __init__(self, movimiento_service: MovimientoService) -> None:
        super().__init__()
        self.movimiento_service = movimiento_service

        self.busqueda_input = QLineEdit()
        self.busqueda_input.setPlaceholderText("Buscar por codigo o nombre")
        self.tipo_combo = QComboBox()
        self.tipo_combo.addItem("Todos", "todos")
        self.tipo_combo.addItem("Entradas", "entrada")
        self.tipo_combo.addItem("Salidas", "salida")

        self.table = QTableWidget(0, 8)
        self.table.setHorizontalHeaderLabels(
            [
                "ID",
                "Codigo",
                "Nombre",
                "Movimiento",
                "Tipo",
                "Cantidad",
                "Usuario",
                "Fecha",
            ]
        )

        self._build_ui()
        self._load_movimientos()

    def _build_ui(self) -> None:
        filtros_layout = QHBoxLayout()
        filtros_layout.addWidget(QLabel("Buscar"))
        filtros_layout.addWidget(self.busqueda_input)
        filtros_layout.addWidget(QLabel("Movimiento"))
        filtros_layout.addWidget(self.tipo_combo)

        buscar_button = QPushButton("Filtrar")
        buscar_button.clicked.connect(self._load_movimientos)
        filtros_layout.addWidget(buscar_button)

        self.busqueda_input.returnPressed.connect(self._load_movimientos)
        self.tipo_combo.currentIndexChanged.connect(self._load_movimientos)

        container = QVBoxLayout()
        container.addLayout(filtros_layout)
        container.addWidget(self.table)
        self.setLayout(container)

    def _load_movimientos(self) -> None:
        movimientos = self.movimiento_service.listar_movimientos(
            texto=self.busqueda_input.text(),
            tipo_movimiento=str(self.tipo_combo.currentData()),
        )
        self.table.setRowCount(len(movimientos))

        for row, movimiento in enumerate(movimientos):
            values = [
                str(movimiento.id),
                movimiento.codigo_producto,
                movimiento.nombre_producto,
                movimiento.tipo_movimiento,
                movimiento.tipo,
                str(movimiento.cantidad),
                movimiento.usuario,
                movimiento.fecha,
            ]
            for column, value in enumerate(values):
                self.table.setItem(row, column, QTableWidgetItem(value))

        self.table.resizeColumnsToContents()
