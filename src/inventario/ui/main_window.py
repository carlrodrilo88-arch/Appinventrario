from __future__ import annotations

from PySide6.QtWidgets import QMainWindow, QTabWidget

from inventario.modules.entradas.service import EntradaService
from inventario.modules.movimientos.service import MovimientoService
from inventario.modules.productos.service import ProductoService
from inventario.modules.reportes.service import ReporteService
from inventario.modules.salidas.service import SalidaService
from inventario.modules.usuarios.service import UsuarioService
from inventario.ui.entradas_widget import EntradasWidget
from inventario.ui.movimientos_widget import MovimientosWidget
from inventario.ui.productos_widget import ProductosWidget
from inventario.ui.reportes_widget import ReportesWidget
from inventario.ui.salidas_widget import SalidasWidget


class MainWindow(QMainWindow):
    def __init__(
        self,
        producto_service: ProductoService,
        entrada_service: EntradaService,
        movimiento_service: MovimientoService,
        reporte_service: ReporteService,
        salida_service: SalidaService,
        usuario_service: UsuarioService,
    ) -> None:
        super().__init__()
        self.setWindowTitle("Sistema de Inventario")
        self.resize(960, 600)

        tabs = QTabWidget()
        tabs.addTab(ProductosWidget(producto_service), "Productos")
        tabs.addTab(
            EntradasWidget(entrada_service, producto_service, usuario_service),
            "Entradas",
        )
        tabs.addTab(
            SalidasWidget(salida_service, producto_service, usuario_service),
            "Salidas",
        )
        tabs.addTab(MovimientosWidget(movimiento_service), "Movimientos")
        tabs.addTab(ReportesWidget(reporte_service), "Reportes")
        self.setCentralWidget(tabs)
