from __future__ import annotations

from pathlib import Path

from inventario.db.init_db import initialize_database
from inventario.db.session import SessionLocal
from inventario.config import SALIDAS_PDF_DIR
from inventario.modules.entradas.service import EntradaService
from inventario.modules.movimientos.service import MovimientoService
from inventario.modules.productos.service import ProductoService
from inventario.modules.reportes.service import ReporteService
from inventario.modules.salidas.service import SalidaService
from inventario.modules.usuarios.service import UsuarioService


def _run_gui() -> int:
    from PySide6.QtWidgets import QApplication

    from inventario.ui.main_window import MainWindow

    app = QApplication([])
    session = SessionLocal()
    producto_service = ProductoService(session)
    entrada_service = EntradaService(session)
    movimiento_service = MovimientoService(session)
    reporte_service = ReporteService(session)
    salida_service = SalidaService(session, SALIDAS_PDF_DIR)
    usuario_service = UsuarioService(session)
    usuario_service.asegurar_usuario_admin()
    window = MainWindow(
        producto_service,
        entrada_service,
        movimiento_service,
        reporte_service,
        salida_service,
        usuario_service,
    )
    window.show()
    return app.exec()


def main() -> int:
    db_path = Path("database") / "inventario.db"
    initialize_database(db_path)
    try:
        return _run_gui()
    except ImportError:
        print(f"Base de datos lista en: {db_path.resolve()}")
        print("PySide6 no esta instalado. La interfaz grafica aun no puede abrirse.")
        return 0
