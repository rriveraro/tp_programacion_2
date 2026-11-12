#mascota.py

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from paseos.mascotas.enums import Tamaño
from datetime import date
from paseos.core.database import Base

class Mascota(Base):
    """Representa una mascota que puede ser paseada."""

    __tablename__ = "mascotas"

    id: Mapped[int] = mapped_column(primary_key=True)
    dueno_id: Mapped[int] = mapped_column(ForeignKey('usuarios.id'))
    nombre: Mapped[str]
    fecha_nacimiento: Mapped[date]
    tamaño: Mapped[Tamaño]
    raza: Mapped[str]

    def edad(self, hoy: date) -> int:
        """Edad en años cumplidos a la fecha `hoy`
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

    def tiene_antirrabica_vigente(self, fecha_turno: date) -> bool:
        """Devuelve True si la mascota tiene la vacuna antirrábica vigente a la fecha del turno."""
        # La vacuna dura un año, así que se considera vigente si fue aplicada hace menos de un año.
        return (fecha_turno - self.fecha_nacimiento).days < 365
