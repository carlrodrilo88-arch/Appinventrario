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

from inventario.modules.productos.service import ProductoService
from inventario.modules.salidas.service import SalidaData, SalidaService
from inventario.modules.usuarios.service import UsuarioService
from inventario.config import SALIDAS_PDF_DIR
from inventario.utils import open_file


class SalidasWidget(QWidget):
    def __init__(
        self,
        salida_service: SalidaService,
        producto_service: ProductoService,
        usuario_service: UsuarioService,
    ) -> None:
        super().__init__()
        self.salida_service = salida_service
        self.producto_service = producto_service
        self.usuario_service = usuario_service

        self.producto_combo = QComboBox()
        self.cantidad_input = QSpinBox()
        self.tipo_input = QLineEdit()
        self.usuario_combo = QComboBox()
        self.observacion_input = QLineEdit()
        self.table = QTableWidget(0, 7)
        self.table.setHorizontalHeaderLabels(
            ["ID", "Producto", "Cantidad", "Tipo de salida", "Usuario", "Fecha", "PDF"]
        )

        self.cantidad_input.setRange(1, 1_000_000)
        self.tipo_input.setPlaceholderText("Ejemplo: venta, dano, ajuste")

        self._build_ui()
        self._load_form_data()
        self._load_salidas()

    def _build_ui(self) -> None:
        form_layout = QFormLayout()
        form_layout.addRow("Producto", self.producto_combo)
        form_layout.addRow("Cantidad", self.cantidad_input)
        form_layout.addRow("Tipo de salida", self.tipo_input)
        form_layout.addRow("Usuario", self.usuario_combo)
        form_layout.addRow("Observacion", self.observacion_input)

        form_box = QGroupBox("Registrar salida")
        form_box.setLayout(form_layout)

        guardar_button = QPushButton("Guardar salida")
        guardar_button.clicked.connect(self._guardar_salida)
        abrir_button = QPushButton("Abrir PDF seleccionado")
        abrir_button.clicked.connect(self._abrir_pdf_seleccionado)

        top_layout = QHBoxLayout()
        top_layout.addWidget(form_box)
        botones_layout = QVBoxLayout()
        botones_layout.addWidget(guardar_button)
        botones_layout.addWidget(abrir_button)
        botones_layout.addStretch()
        top_layout.addLayout(botones_layout)

        container = QVBoxLayout()
        container.addLayout(top_layout)
        container.addWidget(QLabel("Historial de salidas"))
        container.addWidget(self.table)
        self.setLayout(container)

    def _load_form_data(self) -> None:
        self.producto_combo.clear()
        for producto in self.producto_service.listar_productos(solo_activos=True):
            label = f"{producto.codigo} - {producto.nombre} (stock: {producto.stock_actual})"
            self.producto_combo.addItem(label, producto.id)

        self.usuario_combo.clear()
        for usuario in self.usuario_service.listar_activos():
            self.usuario_combo.addItem(usuario.usuario, usuario.id)

    def _guardar_salida(self) -> None:
        if self.producto_combo.count() == 0:
            QMessageBox.warning(self, "Salidas", "No hay productos activos disponibles.")
            return
        if self.usuario_combo.count() == 0:
            QMessageBox.warning(self, "Salidas", "No hay usuarios activos disponibles.")
            return
        if not self.tipo_input.text().strip():
            QMessageBox.warning(self, "Salidas", "El tipo de salida es obligatorio.")
            return

        try:
            _, pdf_path = self.salida_service.crear_salida(
                SalidaData(
                    producto_id=int(self.producto_combo.currentData()),
                    cantidad=self.cantidad_input.value(),
                    tipo_salida=self.tipo_input.text(),
                    usuario_id=int(self.usuario_combo.currentData()),
                    observacion=self.observacion_input.text(),
                )
            )
        except ValueError as exc:
            QMessageBox.warning(self, "Salidas", str(exc))
            return

        self.cantidad_input.setValue(1)
        self.tipo_input.clear()
        self.observacion_input.clear()
        self._load_form_data()
        self._load_salidas()
        QMessageBox.information(self, "Salidas", f"Salida registrada. PDF generado en:\n{pdf_path}")

    def _load_salidas(self) -> None:
        salidas = self.salida_service.listar_salidas()
        self.table.setRowCount(len(salidas))

        for row, salida in enumerate(salidas):
            values = [
                str(salida.id),
                salida.producto.nombre,
                str(salida.cantidad),
                salida.tipo_salida,
                salida.usuario_rel.usuario,
                str(salida.fecha),
                f"salida_{salida.id:06d}.pdf",
            ]
            for column, value in enumerate(values):
                self.table.setItem(row, column, QTableWidgetItem(value))

        self.table.resizeColumnsToContents()

    def _abrir_pdf_seleccionado(self) -> None:
        selected_items = self.table.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Salidas", "Selecciona una salida para abrir su PDF.")
            return

        row = selected_items[0].row()
        pdf_name = self.table.item(row, 6).text()
        pdf_path = SALIDAS_PDF_DIR / pdf_name

        try:
            open_file(pdf_path)
        except FileNotFoundError as exc:
            QMessageBox.warning(self, "Salidas", str(exc))
        except OSError as exc:
            QMessageBox.warning(self, "Salidas", f"No se pudo abrir el PDF: {exc}")
