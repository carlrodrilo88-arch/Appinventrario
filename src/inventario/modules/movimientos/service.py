from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy import text
from sqlalchemy.orm import Session


@dataclass(slots=True)
class MovimientoRecord:
    id: int
    producto_id: int
    codigo_producto: str
    nombre_producto: str
    tipo_movimiento: str
    tipo: str
    cantidad: int
    fecha: str
    usuario: str
    observacion: str
    stock_resultante: str | None
    ultima_actualizacion: str


class MovimientoService:
    def __init__(self, session: Session) -> None:
        self.session = session

    def listar_movimientos(
        self,
        *,
        texto: str = "",
        tipo_movimiento: str = "todos",
    ) -> list[MovimientoRecord]:
        sql = """
        SELECT
            id,
            producto_id,
            codigo_producto,
            nombre_producto,
            tipo_movimiento,
            tipo,
            cantidad,
            fecha,
            usuario,
            observacion,
            stock_resultante,
            ultima_actualizacion
        FROM movimientos
        WHERE (:texto = '' OR codigo_producto LIKE :criterio OR nombre_producto LIKE :criterio)
          AND (:tipo_movimiento = 'todos' OR tipo_movimiento = :tipo_movimiento)
        ORDER BY fecha DESC, id DESC
        """
        criterio = f"%{texto.strip()}%"
        rows = self.session.execute(
            text(sql),
            {
                "texto": texto.strip(),
                "criterio": criterio,
                "tipo_movimiento": tipo_movimiento,
            },
        ).mappings()
        return [MovimientoRecord(**row) for row in rows]
