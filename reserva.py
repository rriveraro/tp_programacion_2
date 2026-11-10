# reserva.py
from datetime import datetime, timedelta

from config import MINUTOS_CANCELACION_TARDIA
from enums import EstadoReserva
from estados import ESTADOS
from turno import Turno


class Reserva:
    """Reserva de un paseo. El comportamiento depende del estado (patrón State)."""

    def __init__(self, mascota_id: int, turno: Turno):
        self.mascota_id = mascota_id
        self.turno = turno
        self.estado = EstadoReserva.PENDIENTE
        self.paseador_id: int | None = None
        self.devuelta_en: datetime | None = None
        self.devolucion_tardia = False

    @property
    def _state(self):
        return ESTADOS[self.estado]

    def aceptar(self, paseador_id: int, ahora: datetime) -> None:
        self._state.aceptar(self, paseador_id, ahora)

    def cancelar_por_dueno(self, ahora: datetime) -> None:
        self._state.cancelar_por_dueno(self, ahora)

    def cancelar_aceptacion(self, ahora: datetime) -> None:
        self._state.cancelar_aceptacion(self, ahora)

    def expirar(self, ahora: datetime) -> None:
        self._state.expirar(self, ahora)

    def finalizar(self, ahora: datetime) -> None:
        self._state.finalizar(self, ahora)

    def es_cancelacion_tardia(self, ahora: datetime) -> bool:
        limite = self.turno.inicio - timedelta(minutes=MINUTOS_CANCELACION_TARDIA)
        return ahora >= limite