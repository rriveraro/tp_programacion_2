# estados.py
from __future__ import annotations

from datetime import timedelta

from config import MINUTOS_EXPIRAR_ANTES
from paseos.reservas.enums import EstadoReserva
from paseos.pagos.excepciones import TransicionInvalidaError


class ReservaState:

    def _prohibido(self, reserva, accion: str):
        raise TransicionInvalidaError(
            f"No se puede {accion} una reserva en estado {reserva.estado.value}"
        )

    def aceptar(self, reserva, paseador_id, ahora):
        self._prohibido(reserva, "aceptar")

    def cancelar_por_dueno(self, reserva, ahora):
        self._prohibido(reserva, "cancelar")

    def cancelar_aceptacion(self, reserva, ahora):
        self._prohibido(reserva, "retirar la aceptación de")

    def expirar(self, reserva, ahora):
        self._prohibido(reserva, "expirar")

    def finalizar(self, reserva, ahora):
        self._prohibido(reserva, "finalizar")


def _limite_de_vencimiento(reserva):
    """Momento desde el cual una reserva pendiente se considera vencida."""
    return reserva.turno.inicio - timedelta(minutes=MINUTOS_EXPIRAR_ANTES)


class PendienteState(ReservaState):
    def aceptar(self, reserva, paseador_id, ahora):
        if ahora >= _limite_de_vencimiento(reserva):
            raise TransicionInvalidaError("La reserva ya venció, no se puede aceptar")
        reserva.paseador_id = paseador_id
        reserva.estado = EstadoReserva.ACEPTADA

    def cancelar_por_dueno(self, reserva, ahora):
        reserva.estado = EstadoReserva.CANCELADA

    def expirar(self, reserva, ahora):
        if ahora < _limite_de_vencimiento(reserva):
            raise TransicionInvalidaError("La reserva todavía no venció")
        reserva.estado = EstadoReserva.EXPIRADA


class AceptadaState(ReservaState):
    def cancelar_por_dueno(self, reserva, ahora):
        reserva.estado = EstadoReserva.CANCELADA

    def cancelar_aceptacion(self, reserva, ahora):
        # El servicio tiene que guardar el paseador_id ANTES de llamar acá,
        # para saber a quién penalizar.
        reserva.paseador_id = None
        reserva.estado = EstadoReserva.PENDIENTE

    def finalizar(self, reserva, ahora):
        reserva.devuelta_en = ahora
        reserva.devolucion_tardia = ahora > reserva.turno.fin
        reserva.estado = EstadoReserva.FINALIZADA


class CanceladaState(ReservaState):
    """Estado final: no permite ninguna acción."""


class ExpiradaState(ReservaState):
    """Estado final: no permite ninguna acción."""


class FinalizadaState(ReservaState):
    """Estado final: no permite ninguna acción."""


# El enum es lo que se guarda en la base de datos y del cual se elige el objeto estado.
ESTADOS = {
    EstadoReserva.PENDIENTE: PendienteState(),
    EstadoReserva.ACEPTADA: AceptadaState(),
    EstadoReserva.CANCELADA: CanceladaState(),
    EstadoReserva.EXPIRADA: ExpiradaState(),
    EstadoReserva.FINALIZADA: FinalizadaState(),
}