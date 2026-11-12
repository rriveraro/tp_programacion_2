"""Schemas Pydantic: definen qué datos entran y salen por la API.

Los modelos (models.py) son la tabla; los schemas son el "contrato" con el
cliente. Por eso `password_hash` nunca aparece en un schema de salida.
"""

from datetime import date

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

from paseos.usuarios.enums import Barrio, Rol


class UsuarioCrear(BaseModel):
    """Datos para registrar un usuario. Lo usa el registro (auth)."""

    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    nombre: str = Field(min_length=2, max_length=100)
    dni: str = Field(
        pattern=r'^\d{7,8}$', description='Solo números, 7 u 8 dígitos'
    )
    fecha_nacimiento: date
    calle: str = Field(min_length=2, max_length=100)
    numero: str = Field(min_length=1, max_length=10)
    barrio: Barrio
    rol: Rol

    @field_validator('email')
    @classmethod
    def email_en_minuscula(cls, valor: str) -> str:
        return valor.lower()


class UsuarioActualizar(BaseModel):
    """Datos editables del propio usuario.

    Email, DNI, rol y fecha de nacimiento NO se pueden cambiar: si el cliente
    los envía, `extra="forbid"` responde 422. La contraseña se cambia por
    otro endpoint (auth).
    """

    model_config = ConfigDict(extra='forbid')

    nombre: str | None = Field(default=None, min_length=2, max_length=100)
    calle: str | None = Field(default=None, min_length=2, max_length=100)
    numero: str | None = Field(default=None, min_length=1, max_length=10)
    barrio: Barrio | None = None


class UsuarioPublico(BaseModel):
    """Lo que la API devuelve de un usuario (sin contraseña)."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    email: EmailStr
    nombre: str
    dni: str
    fecha_nacimiento: date
    calle: str
    numero: str
    barrio: Barrio
    rol: Rol
    activo: bool
