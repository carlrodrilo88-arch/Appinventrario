from __future__ import annotations

from datetime import datetime

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class Producto(Base):
    __tablename__ = "productos"
    __table_args__ = (
        CheckConstraint("stock_actual >= 0", name="ck_productos_stock_actual"),
        CheckConstraint("stock_minimo >= 0", name="ck_productos_stock_minimo"),
        CheckConstraint("activo IN (0, 1)", name="ck_productos_activo"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    codigo: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    nombre: Mapped[str] = mapped_column(String, nullable=False)
    unidad_medida: Mapped[str] = mapped_column(String, nullable=False)
    stock_actual: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    stock_minimo: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    activo: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    ultima_actualizacion: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    entradas: Mapped[list["Entrada"]] = relationship(back_populates="producto")
    salidas: Mapped[list["Salida"]] = relationship(back_populates="producto")


class Usuario(Base):
    __tablename__ = "usuarios"
    __table_args__ = (CheckConstraint("activo IN (0, 1)", name="ck_usuarios_activo"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nombre: Mapped[str] = mapped_column(String, nullable=False)
    usuario: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    contrasena_hash: Mapped[str] = mapped_column(String, nullable=False)
    activo: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    ultima_actualizacion: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    entradas: Mapped[list["Entrada"]] = relationship(back_populates="usuario_rel")
    salidas: Mapped[list["Salida"]] = relationship(back_populates="usuario_rel")


class Entrada(Base):
    __tablename__ = "entradas"
    __table_args__ = (CheckConstraint("cantidad > 0", name="ck_entradas_cantidad"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    producto_id: Mapped[int] = mapped_column(ForeignKey("productos.id"), nullable=False)
    cantidad: Mapped[int] = mapped_column(Integer, nullable=False)
    fecha: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    tipo_entrada: Mapped[str] = mapped_column(String, nullable=False)
    observacion: Mapped[str] = mapped_column(Text, nullable=False, default="")
    usuario_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id"), nullable=False)
    ultima_actualizacion: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    producto: Mapped[Producto] = relationship(back_populates="entradas")
    usuario_rel: Mapped[Usuario] = relationship(back_populates="entradas")


class Salida(Base):
    __tablename__ = "salidas"
    __table_args__ = (CheckConstraint("cantidad > 0", name="ck_salidas_cantidad"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    producto_id: Mapped[int] = mapped_column(ForeignKey("productos.id"), nullable=False)
    cantidad: Mapped[int] = mapped_column(Integer, nullable=False)
    fecha: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    tipo_salida: Mapped[str] = mapped_column(String, nullable=False)
    observacion: Mapped[str] = mapped_column(Text, nullable=False, default="")
    usuario_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id"), nullable=False)
    ultima_actualizacion: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    producto: Mapped[Producto] = relationship(back_populates="salidas")
    usuario_rel: Mapped[Usuario] = relationship(back_populates="salidas")
