from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from inventario.db.models import Producto


@dataclass(slots=True)
class ProductoData:
    codigo: str
    nombre: str
    unidad_medida: str
    stock_actual: int = 0
    stock_minimo: int = 0
    activo: int = 1


class ProductoService:
    def __init__(self, session: Session) -> None:
        self.session = session

    def crear_producto(self, data: ProductoData) -> Producto:
        producto = Producto(
            codigo=data.codigo.strip(),
            nombre=data.nombre.strip(),
            unidad_medida=data.unidad_medida.strip(),
            stock_actual=data.stock_actual,
            stock_minimo=data.stock_minimo,
            activo=data.activo,
        )
        self.session.add(producto)
        try:
            self.session.commit()
        except IntegrityError as exc:
            self.session.rollback()
            raise ValueError("No se pudo crear el producto. Verifica codigo unico y datos.") from exc
        self.session.refresh(producto)
        return producto

    def listar_productos(self, solo_activos: bool = False) -> list[Producto]:
        query = select(Producto).order_by(Producto.nombre.asc())
        if solo_activos:
            query = query.where(Producto.activo == 1)
        return list(self.session.scalars(query))

    def buscar_productos(self, texto: str, solo_activos: bool = False) -> list[Producto]:
        criterio = f"%{texto.strip()}%"
        query = (
            select(Producto)
            .where((Producto.codigo.like(criterio)) | (Producto.nombre.like(criterio)))
            .order_by(Producto.nombre.asc())
        )
        if solo_activos:
            query = query.where(Producto.activo == 1)
        return list(self.session.scalars(query))

    def buscar_por_codigo(self, codigo: str) -> Producto | None:
        query = select(Producto).where(Producto.codigo == codigo.strip())
        return self.session.scalar(query)

    def actualizar_producto(
        self,
        producto_id: int,
        *,
        nombre: str,
        unidad_medida: str,
        stock_minimo: int,
        activo: int,
    ) -> Producto:
        producto = self.session.get(Producto, producto_id)
        if producto is None:
            raise ValueError("Producto no encontrado.")

        producto.nombre = nombre.strip()
        producto.unidad_medida = unidad_medida.strip()
        producto.stock_minimo = stock_minimo
        producto.activo = activo
        producto.ultima_actualizacion = datetime.utcnow()

        self.session.commit()
        self.session.refresh(producto)
        return producto

    def desactivar_producto(self, producto_id: int) -> Producto:
        producto = self.session.get(Producto, producto_id)
        if producto is None:
            raise ValueError("Producto no encontrado.")

        producto.activo = 0
        producto.ultima_actualizacion = datetime.utcnow()
        self.session.commit()
        self.session.refresh(producto)
        return producto
