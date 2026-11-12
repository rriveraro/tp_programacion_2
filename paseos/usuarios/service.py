"""Reglas de negocio de usuarios.

El servicio no sabe nada de HTTP: recibe datos, aplica reglas y lanza
excepciones de negocio (ver exceptions.py) cuando algo no se cumple.
"""

from collections.abc import Callable
from datetime import date

from paseos.usuarios.exceptions import (
    DniYaRegistrado,
    EmailYaRegistrado,
    SinCambios,
    UsuarioConReservasActivas,
    UsuarioNoEncontrado,
)
from paseos.usuarios.models import Usuario
from paseos.usuarios.repository import UsuarioRepository
from paseos.usuarios.schemas import UsuarioActualizar, UsuarioCrear

# Función que responde "¿este usuario tiene reservas PENDIENTE o ACEPTADA?".
VerificadorReservas = Callable[[Usuario], bool]


def _sin_reservas(_: Usuario) -> bool:
    # TODO(reservas): reemplazar por la consulta real cuando exista el módulo
    # reservas. Para un dueño cuentan las reservas de sus mascotas; para un
    # paseador, las que aceptó.
    return False


class UsuarioService:
    def __init__(
        self,
        repo: UsuarioRepository,
        tiene_reservas_activas: VerificadorReservas = _sin_reservas,
    ):
        self.repo = repo
        self.tiene_reservas_activas = tiene_reservas_activas

    def crear_usuario(
        self, datos: UsuarioCrear, password_hash: str, hoy: date
    ) -> Usuario:
        """Crea un usuario nuevo. Lo llama el registro (módulo auth).

        Recibe la contraseña YA hasheada: hashear es responsabilidad de auth.
        """
        if self.repo.obtener_por_email(datos.email):
            raise EmailYaRegistrado()
        if self.repo.obtener_por_dni(datos.dni):
            raise DniYaRegistrado()

        usuario = Usuario(
            **datos.model_dump(exclude={'password'}),
            password_hash=password_hash,
            activo=True,
        )
        usuario.validar_edad(hoy)
        return self.repo.guardar(usuario)

    def obtener_por_id(self, usuario_id: int) -> Usuario:
        usuario = self.repo.obtener_por_id(usuario_id)
        if usuario is None or not usuario.activo:
            raise UsuarioNoEncontrado()
        return usuario

    def obtener_activo_por_email(self, email: str) -> Usuario | None:
        """Para el login: devuelve None si no existe o está dado de baja."""
        usuario = self.repo.obtener_por_email(email)
        return usuario if usuario and usuario.activo else None

    def actualizar(
        self, usuario: Usuario, cambios: UsuarioActualizar
    ) -> Usuario:
        """Modifica nombre y/o domicilio.

        Cambiar el domicilio NO altera las reservas ya creadas, porque cada
        reserva guarda su propia copia de calle, número y barrio.
        """
        datos = cambios.model_dump(exclude_unset=True, exclude_none=True)
        if not datos:
            raise SinCambios()
        for campo, valor in datos.items():
            setattr(usuario, campo, valor)
        return self.repo.guardar(usuario)

    def dar_de_baja(self, usuario: Usuario) -> None:
        """Baja lógica. Se rechaza (409) si tiene reservas activas."""
        if self.tiene_reservas_activas(usuario):
            raise UsuarioConReservasActivas()
        usuario.dar_de_baja()
        self.repo.guardar(usuario)
