from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from inventario.db.models import Producto, Salida
from inventario.reports.pdf import generar_pdf_salida


@dataclass(slots=True)
class SalidaData:
    producto_id: int
    cantidad: int
    tipo_salida: str
    usuario_id: int
    observacion: str = ""


class SalidaService:
    def __init__(self, session: Session, pdf_dir: Path) -> None:
        self.session = session
        self.pdf_dir = pdf_dir

    def crear_salida(self, data: SalidaData) -> tuple[Salida, Path]:
        producto = self.session.get(Producto, data.producto_id)
        if producto is None:
            raise ValueError("Producto no encontrado.")
        if producto.activo != 1:
            raise ValueError("No se puede registrar salida para un producto inactivo.")

        salida = Salida(
            producto_id=data.producto_id,
            cantidad=data.cantidad,
            tipo_salida=data.tipo_salida.strip(),
            observacion=data.observacion.strip(),
            usuario_id=data.usuario_id,
        )
        self.session.add(salida)
        try:
            self.session.commit()
        except IntegrityError as exc:
            self.session.rollback()
            raise ValueError("No se pudo registrar la salida.") from exc
        except Exception as exc:
            self.session.rollback()
            message = str(exc)
            if "Stock insuficiente" in message:
                raise ValueError("Stock insuficiente para registrar la salida.") from exc
            raise

        self.session.refresh(salida)
        self.session.refresh(producto)

        pdf_path = generar_pdf_salida(salida, producto, salida.usuario_rel, self.pdf_dir)
        return salida, pdf_path

    def listar_salidas(self) -> list[Salida]:
        query = select(Salida).order_by(Salida.fecha.desc(), Salida.id.desc())
        return list(self.session.scalars(query))
