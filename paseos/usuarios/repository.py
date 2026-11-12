"""Acceso a datos de usuarios.

El repositorio es la única capa que habla con SQLAlchemy. El servicio le pide
cosas ("buscá por email", "guardá") sin saber cómo se hacen las consultas.
"""

from sqlalchemy import select
from sqlalchemy.orm import Session

from paseos.usuarios.models import Usuario


class UsuarioRepository:
    def __init__(self, db: Session):
        self.db = db

    def obtener_por_id(self, usuario_id: int) -> Usuario | None:
        return self.db.get(Usuario, usuario_id)

    def obtener_por_email(self, email: str) -> Usuario | None:
        return self.db.scalar(
            select(Usuario).where(Usuario.email == email.lower())
        )

    def obtener_por_dni(self, dni: str) -> Usuario | None:
        return self.db.scalar(select(Usuario).where(Usuario.dni == dni))

    def guardar(self, usuario: Usuario) -> Usuario:
        """Inserta o actualiza el usuario y confirma la transacción."""
        self.db.add(usuario)
        self.db.commit()
        self.db.refresh(usuario)
        return usuario
