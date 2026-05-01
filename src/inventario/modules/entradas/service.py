from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.orm import Session

from inventario.db.models import Entrada, Producto


@dataclass(slots=True)
class EntradaData:
    producto_id: int
    cantidad: int
    tipo_entrada: str
    usuario_id: int
    observacion: str = ""


class EntradaService:
    def __init__(self, session: Session) -> None:
        self.session = session

    def crear_entrada(self, data: EntradaData) -> Entrada:
        producto = self.session.get(Producto, data.producto_id)
        if producto is None:
            raise ValueError("Producto no encontrado.")
        if producto.activo != 1:
            raise ValueError("No se puede registrar entrada para un producto inactivo.")

        entrada = Entrada(
            producto_id=data.producto_id,
            cantidad=data.cantidad,
            tipo_entrada=data.tipo_entrada.strip(),
            observacion=data.observacion.strip(),
            usuario_id=data.usuario_id,
        )
        self.session.add(entrada)
        self.session.commit()
        self.session.refresh(entrada)
        return entrada

    def listar_entradas(self) -> list[Entrada]:
        query = select(Entrada).order_by(Entrada.fecha.desc(), Entrada.id.desc())
        return list(self.session.scalars(query))
