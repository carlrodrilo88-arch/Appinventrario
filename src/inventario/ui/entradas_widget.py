from __future__ import annotations

from PySide6.QtWidgets import (
    QComboBox,
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

from inventario.modules.entradas.service import EntradaData, EntradaService
from inventario.modules.productos.service import ProductoService
from inventario.modules.usuarios.service import UsuarioService


class EntradasWidget(QWidget):
    def __init__(
        self,
        entrada_service: EntradaService,
        producto_service: ProductoService,
        usuario_service: UsuarioService,
    ) -> None:
        super().__init__()
        self.entrada_service = entrada_service
        self.producto_service = producto_service
        self.usuario_service = usuario_service

        self.producto_combo = QComboBox()
        self.cantidad_input = QSpinBox()
        self.tipo_input = QLineEdit()
        self.usuario_combo = QComboBox()
        self.observacion_input = QLineEdit()
        self.table = QTableWidget(0, 6)
        self.table.setHorizontalHeaderLabels(
            ["ID", "Producto", "Cantidad", "Tipo de entrada", "Usuario", "Fecha"]
        )

        self.cantidad_input.setRange(1, 1_000_000)
        self.tipo_input.setPlaceholderText("Ejemplo: compra, ajuste, devolucion")

        self._build_ui()
        self._load_form_data()
        self._load_entradas()

    def _build_ui(self) -> None:
        form_layout = QFormLayout()
        form_layout.addRow("Producto", self.producto_combo)
        form_layout.addRow("Cantidad", self.cantidad_input)
        form_layout.addRow("Tipo de entrada", self.tipo_input)
        form_layout.addRow("Usuario", self.usuario_combo)
        form_layout.addRow("Observacion", self.observacion_input)

        form_box = QGroupBox("Registrar entrada")
        form_box.setLayout(form_layout)

        guardar_button = QPushButton("Guardar entrada")
        guardar_button.clicked.connect(self._guardar_entrada)

        top_layout = QHBoxLayout()
        top_layout.addWidget(form_box)
        top_layout.addWidget(guardar_button)

        container = QVBoxLayout()
        container.addLayout(top_layout)
        container.addWidget(QLabel("Historial de entradas"))
        container.addWidget(self.table)
        self.setLayout(container)

    def _load_form_data(self) -> None:
        self.producto_combo.clear()
        for producto in self.producto_service.listar_productos(solo_activos=True):
            self.producto_combo.addItem(f"{producto.codigo} - {producto.nombre}", producto.id)

        self.usuario_combo.clear()
        for usuario in self.usuario_service.listar_activos():
            self.usuario_combo.addItem(usuario.usuario, usuario.id)

    def _guardar_entrada(self) -> None:
        if self.producto_combo.count() == 0:
            QMessageBox.warning(self, "Entradas", "No hay productos activos disponibles.")
            return
        if self.usuario_combo.count() == 0:
            QMessageBox.warning(self, "Entradas", "No hay usuarios activos disponibles.")
            return
        if not self.tipo_input.text().strip():
            QMessageBox.warning(self, "Entradas", "El tipo de entrada es obligatorio.")
            return

        try:
            self.entrada_service.crear_entrada(
                EntradaData(
                    producto_id=int(self.producto_combo.currentData()),
                    cantidad=self.cantidad_input.value(),
                    tipo_entrada=self.tipo_input.text(),
                    usuario_id=int(self.usuario_combo.currentData()),
                    observacion=self.observacion_input.text(),
                )
            )
        except ValueError as exc:
            QMessageBox.warning(self, "Entradas", str(exc))
            return

        self.cantidad_input.setValue(1)
        self.tipo_input.clear()
        self.observacion_input.clear()
        self._load_form_data()
        self._load_entradas()

    def _load_entradas(self) -> None:
        entradas = self.entrada_service.listar_entradas()
        self.table.setRowCount(len(entradas))

        for row, entrada in enumerate(entradas):
            values = [
                str(entrada.id),
                entrada.producto.nombre,
                str(entrada.cantidad),
                entrada.tipo_entrada,
                entrada.usuario_rel.usuario,
                str(entrada.fecha),
            ]
            for column, value in enumerate(values):
                self.table.setItem(row, column, QTableWidgetItem(value))

        self.table.resizeColumnsToContents()
