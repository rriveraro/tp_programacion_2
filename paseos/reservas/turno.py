# turno.py
from dataclasses import dataclass
from datetime import date, datetime, time
from paseos.pagos.excepciones import TurnoInvalidoError

@dataclass(Frozen=True)

class Turno:
    """Franja de un paseo: un día, una hora de salida y una de llegada."""

    fecha: date
    hora_inicio: time
    hora_fin: time
 
    def __post_init__(self):
        if self.hora_fin <= self.hora_inicio:
            raise TurnoInvalidoError("El turno no puede terminar antes de empezar")

    @property
    def inicio(self) -> datetime:
        return datetime.combine(self.fecha, self.hora_inicio)

    @property
    def fin(self) -> datetime:
        return datetime.combine(self.fecha, self.hora_fin)

    def validar_turno(self, ahora: datetime) -> None:
        """Regla que depende del tiempo: `ahora` llega desde afuera para poder testearla."""
        if self.inicio <= ahora:
            raise TurnoInvalidoError("El turno no puede empezar en el pasado")