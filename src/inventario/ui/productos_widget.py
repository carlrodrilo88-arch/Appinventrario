from __future__ import annotations

from PySide6.QtWidgets import (
    QCheckBox,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QSpinBox,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from inventario.modules.productos.service import ProductoData, ProductoService


class ProductosWidget(QWidget):
    def __init__(self, producto_service: ProductoService) -> None:
        super().__init__()
        self.producto_service = producto_service
        self.selected_producto_id: int | None = None

        self.codigo_input = QLineEdit()
        self.nombre_input = QLineEdit()
        self.unidad_input = QLineEdit()
        self.stock_actual_input = QSpinBox()
        self.stock_minimo_input = QSpinBox()
        self.busqueda_input = QLineEdit()
        self.solo_activos_check = QCheckBox("Solo activos")
        self.activo_check = QCheckBox("Activo")
        self.activo_check.setChecked(True)

        self.stock_actual_input.setRange(0, 1_000_000)
        self.stock_minimo_input.setRange(0, 1_000_000)
        self.busqueda_input.setPlaceholderText("Buscar por codigo o nombre")

        self.table = QTableWidget(0, 8)
        self.table.setHorizontalHeaderLabels(
            [
                "ID",
                "Codigo",
                "Nombre",
                "Unidad de medida",
                "Stock actual",
                "Stock minimo",
                "Activo",
                "Ultima actualizacion",
            ]
        )
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.table.itemSelectionChanged.connect(self._cargar_seleccion)

        self.guardar_button = QPushButton("Guardar")
        self.actualizar_button = QPushButton("Actualizar")
        self.desactivar_button = QPushButton("Desactivar")
        self.limpiar_button = QPushButton("Limpiar")

        self._build_ui()
        self._load_productos()

    def _build_ui(self) -> None:
        form_layout = QFormLayout()
        form_layout.addRow("Codigo", self.codigo_input)
        form_layout.addRow("Nombre", self.nombre_input)
        form_layout.addRow("Unidad de medida", self.unidad_input)
        form_layout.addRow("Stock actual", self.stock_actual_input)
        form_layout.addRow("Stock minimo", self.stock_minimo_input)
        form_layout.addRow("", self.activo_check)

        form_box = QGroupBox("Registrar producto")
        form_box.setLayout(form_layout)

        self.guardar_button.clicked.connect(self._guardar_producto)
        self.actualizar_button.clicked.connect(self._actualizar_producto)
        self.desactivar_button.clicked.connect(self._desactivar_producto)
        self.limpiar_button.clicked.connect(self._limpiar_formulario)
        self.actualizar_button.setEnabled(False)
        self.desactivar_button.setEnabled(False)

        acciones_layout = QVBoxLayout()
        acciones_layout.addWidget(self.guardar_button)
        acciones_layout.addWidget(self.actualizar_button)
        acciones_layout.addWidget(self.desactivar_button)
        acciones_layout.addWidget(self.limpiar_button)
        acciones_layout.addStretch()

        top_layout = QHBoxLayout()
        top_layout.addWidget(form_box)
        top_layout.addLayout(acciones_layout)

        filtros_layout = QHBoxLayout()
        filtros_layout.addWidget(QLabel("Buscar"))
        filtros_layout.addWidget(self.busqueda_input)
        filtros_layout.addWidget(self.solo_activos_check)

        self.busqueda_input.textChanged.connect(self._load_productos)
        self.solo_activos_check.stateChanged.connect(self._load_productos)

        container = QVBoxLayout()
        container.addLayout(top_layout)
        container.addLayout(filtros_layout)
        container.addWidget(QLabel("Listado de productos"))
        container.addWidget(self.table)
        self.setLayout(container)

    def _guardar_producto(self) -> None:
        try:
            self.producto_service.crear_producto(
                ProductoData(
                    codigo=self.codigo_input.text(),
                    nombre=self.nombre_input.text(),
                    unidad_medida=self.unidad_input.text(),
                    stock_actual=self.stock_actual_input.value(),
                    stock_minimo=self.stock_minimo_input.value(),
                    activo=1 if self.activo_check.isChecked() else 0,
                )
            )
        except ValueError as exc:
            QMessageBox.warning(self, "Producto", str(exc))
            return

        self._limpiar_formulario()
        self._load_productos()

    def _actualizar_producto(self) -> None:
        if self.selected_producto_id is None:
            QMessageBox.warning(self, "Producto", "Selecciona un producto para actualizar.")
            return

        try:
            self.producto_service.actualizar_producto(
                self.selected_producto_id,
                nombre=self.nombre_input.text(),
                unidad_medida=self.unidad_input.text(),
                stock_minimo=self.stock_minimo_input.value(),
                activo=1 if self.activo_check.isChecked() else 0,
            )
        except ValueError as exc:
            QMessageBox.warning(self, "Producto", str(exc))
            return

        self._limpiar_formulario()
        self._load_productos()

    def _desactivar_producto(self) -> None:
        if self.selected_producto_id is None:
            QMessageBox.warning(self, "Producto", "Selecciona un producto para desactivar.")
            return

        self.producto_service.desactivar_producto(self.selected_producto_id)
        self._limpiar_formulario()
        self._load_productos()

    def _load_productos(self) -> None:
        texto = self.busqueda_input.text().strip()
        solo_activos = self.solo_activos_check.isChecked()
        if texto:
            productos = self.producto_service.buscar_productos(texto, solo_activos=solo_activos)
        else:
            productos = self.producto_service.listar_productos(solo_activos=solo_activos)
        self.table.setRowCount(len(productos))

        for row, producto in enumerate(productos):
            values = [
                str(producto.id),
                producto.codigo,
                producto.nombre,
                producto.unidad_medida,
                str(producto.stock_actual),
                str(producto.stock_minimo),
                "Si" if producto.activo else "No",
                str(producto.ultima_actualizacion),
            ]
            for column, value in enumerate(values):
                self.table.setItem(row, column, QTableWidgetItem(value))

        self.table.resizeColumnsToContents()

    def _cargar_seleccion(self) -> None:
        selected_items = self.table.selectedItems()
        if not selected_items:
            return

        row = selected_items[0].row()
        self.selected_producto_id = int(self.table.item(row, 0).text())
        self.codigo_input.setText(self.table.item(row, 1).text())
        self.nombre_input.setText(self.table.item(row, 2).text())
        self.unidad_input.setText(self.table.item(row, 3).text())
        self.stock_actual_input.setValue(int(self.table.item(row, 4).text()))
        self.stock_minimo_input.setValue(int(self.table.item(row, 5).text()))
        self.activo_check.setChecked(self.table.item(row, 6).text() == "Si")

        self.codigo_input.setEnabled(False)
        self.stock_actual_input.setEnabled(False)
        self.guardar_button.setEnabled(False)
        self.actualizar_button.setEnabled(True)
        self.desactivar_button.setEnabled(True)

    def _limpiar_formulario(self) -> None:
        self.selected_producto_id = None
        self.codigo_input.clear()
        self.nombre_input.clear()
        self.unidad_input.clear()
        self.stock_actual_input.setValue(0)
        self.stock_minimo_input.setValue(0)
        self.activo_check.setChecked(True)
        self.codigo_input.setEnabled(True)
        self.stock_actual_input.setEnabled(True)
        self.guardar_button.setEnabled(True)
        self.actualizar_button.setEnabled(False)
        self.desactivar_button.setEnabled(False)
        self.table.clearSelection()
