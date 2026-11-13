"""Reglas de autenticación: registro, login y cambio de contraseña."""

from datetime import date

from paseos.auth.exceptions import (
    CredencialesInvalidas,
    PasswordActualIncorrecta,
)
from paseos.core.security import (
    create_access_token,
    get_password_hash,
    verify_password,
)
from paseos.usuarios.models import Usuario
from paseos.usuarios.schemas import UsuarioCrear
from paseos.usuarios.service import UsuarioService


class AuthService:
    def __init__(self, usuarios: UsuarioService):
        self.usuarios = usuarios

    def registrar(self, datos: UsuarioCrear, hoy: date) -> Usuario:
        """Hashea la contraseña y delega la creación en usuarios."""
        password_hash = get_password_hash(datos.password)
        return self.usuarios.crear_usuario(datos, password_hash, hoy)

    def autenticar(self, email: str, password: str) -> Usuario:
        """Comprueba email y contraseña. Devuelve el usuario o lanza error."""
        usuario = self.usuarios.obtener_activo_por_email(email)
        # Mismo error si falla el email o la contraseña: no revela cuál.
        if usuario is None or not verify_password(
            password, usuario.password_hash
        ):
            raise CredencialesInvalidas()
        return usuario

    def login(self, email: str, password: str) -> str:
        """Autentica y devuelve un token de acceso."""
        usuario = self.autenticar(email, password)
        return create_access_token({'sub': usuario.email})

    def cambiar_password(
        self, usuario: Usuario, password_actual: str, password_nueva: str
    ) -> None:
        """Cambia la contraseña de un usuario ya autenticado."""
        if not verify_password(password_actual, usuario.password_hash):
            raise PasswordActualIncorrecta()
        nuevo_hash = get_password_hash(password_nueva)
        self.usuarios.actualizar_password(usuario, nuevo_hash)
