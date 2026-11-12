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
    fecha_antirrabica: Mapped[date | None] = mapped_column(nullable=True)

    def edad(self, hoy: date) -> int:
        """Edad en años cumplidos a la fecha `hoy`
        """
        cumplio_este_year = (hoy.month, hoy.day) >= (
            self.fecha_nacimiento.month,
            self.fecha_nacimiento.day,
        )
        return (
            hoy.year
            - self.fecha_nacimiento.year
            - (0 if cumplio_este_year else 1)
        )

    def tiene_antirrabica_vigente(self, fecha_turno: date) -> bool:
        '''indica si la vacuna antirrábica está vigente a la fecha del turno'''
        if self.fecha_antirrabica is None or fecha_turno < self.fecha_antirrabica:
            return False

        try:
            vencimiento = self.fecha_antirrabica.replace(
                year=self.fecha_antirrabica.year + 1
            )
        except ValueError:  # Aplicación el 29 de febrero
            vencimiento = self.fecha_antirrabica.replace(
                year=self.fecha_antirrabica.year + 1,
                day=28,
            )

        return fecha_turno < vencimiento