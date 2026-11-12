"""Modelo SQLAlchemy de Usuario (tabla `usuarios`)."""

from datetime import date

from sqlalchemy import Boolean, Date, Enum, String
from sqlalchemy.orm import Mapped, mapped_column

from paseos.core.database import Base
from paseos.core.settings import settings
from paseos.usuarios.enums import Barrio, Rol
from paseos.usuarios.exceptions import EdadFueraDeRango


class Usuario(Base):
    """Dueño o paseador de la plataforma.

    No hay subclases Dueño/Paseador: el comportamiento que cambia según el rol
    (por ejemplo, la edad máxima) se resuelve con el enum `Rol` y la
    configuración. Así hay una sola tabla y un solo modelo.
    """

    __tablename__ = 'usuarios'

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    nombre: Mapped[str] = mapped_column(String(100))
    dni: Mapped[str] = mapped_column(String(8), unique=True, index=True)
    fecha_nacimiento: Mapped[date] = mapped_column(Date)
    calle: Mapped[str] = mapped_column(String(100))
    numero: Mapped[str] = mapped_column(String(10))
    barrio: Mapped[Barrio] = mapped_column(Enum(Barrio))
    password_hash: Mapped[str] = mapped_column(String(255))
    rol: Mapped[Rol] = mapped_column(Enum(Rol))
    activo: Mapped[bool] = mapped_column(Boolean, default=True)

    def edad(self, hoy: date) -> int:
        """Edad en años cumplidos a la fecha `hoy`.

        `hoy` se recibe por parámetro (y no con date.today()) para poder
        testear con fechas fijas.
        """
        cumplio_este_anio = (hoy.month, hoy.day) >= (
            self.fecha_nacimiento.month,
            self.fecha_nacimiento.day,
        )
        return (
            hoy.year
            - self.fecha_nacimiento.year
            - (0 if cumplio_este_anio else 1)
        )

    def validar_edad(self, hoy: date) -> None:
        """Lanza EdadFueraDeRango si la edad no está permitida para su rol."""
        edad_maxima = (
            settings.EDAD_MAXIMA_DUENO
            if self.es_dueno()
            else settings.EDAD_MAXIMA_PASEADOR
        )
        edad = self.edad(hoy)
        if not settings.EDAD_MINIMA <= edad <= edad_maxima:
            raise EdadFueraDeRango(
                f'Para el rol {self.rol.value} la edad debe estar entre '
                f'{settings.EDAD_MINIMA} y {edad_maxima} años (tiene {edad})'
            )

    def dar_de_baja(self) -> None:
        """Baja lógica: se marca inactivo y se conserva el historial."""
        self.activo = False

    def es_dueno(self) -> bool:
        return self.rol == Rol.DUENO

    def es_paseador(self) -> bool:
        return self.rol == Rol.PASEADOR
