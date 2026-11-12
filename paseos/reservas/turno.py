# turno.py
from datetime import date, datetime, time
from excepciones import TurnoInvalidoError


class Turno:
    """Franja de un paseo: un día, una hora de salida y una de llegada."""

    def __init__(self, fecha: date, hora_inicio: time, hora_fin: time):
        self.fecha = fecha
        self.hora_inicio = hora_inicio
        self.hora_fin = hora_fin

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