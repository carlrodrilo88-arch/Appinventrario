from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from inventario.db.models import Usuario
from inventario.security import hash_password


class UsuarioService:
    def __init__(self, session: Session) -> None:
        self.session = session

    def asegurar_usuario_admin(self) -> Usuario:
        existente = self.session.scalar(select(Usuario).where(Usuario.usuario == "admin"))
        if existente is not None:
            return existente

        usuario = Usuario(
            nombre="Administrador",
            usuario="admin",
            contrasena_hash=hash_password("admin123"),
            activo=1,
        )
        self.session.add(usuario)
        self.session.commit()
        self.session.refresh(usuario)
        return usuario

    def listar_activos(self) -> list[Usuario]:
        query = select(Usuario).where(Usuario.activo == 1).order_by(Usuario.nombre.asc())
        return list(self.session.scalars(query))
