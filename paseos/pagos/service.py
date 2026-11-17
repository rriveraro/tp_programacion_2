"""Reglas de pagos.

Recibe datos, aplica las relas y lanza excepciones no algo no se cumple.
"""

from datetime import datetime
from typing import TYPE_CHECKING

from paseos.core.exceptions import NoAutorizado
from paseos.pagos.excepciones import (
    PagoNoEncontrado,
    ReservaNoEncontrada,
    ReservaYaPagada,
)
from paseos.pagos.pago import Pago
from paseos.pagos.procesadores import procesar
from paseos.pagos.schemas import CrearPago
from paseos.usuarios.models import Usuario

if TYPE_CHECKING:
    from paseos.pagos.repository import RepositoryPago
    from paseos.reservas.repository import ReservaRepository


class PagoService:
    def __init__(self, repo: 'RepositoryPago', reservas: 'ReservaRepository'):
        self.repo = repo
        self.reservas = reservas

    def crear_pago(
        self, usuario: Usuario, datos: CrearPago, ahora: datetime
    ) -> Pago:
        reserva = self.reservas.obtener_por_id(datos.reserva_id)
        if reserva is None:
            raise ReservaNoEncontrada()
        if reserva.dueno_id != usuario.id:
            raise NoAutorizado('Solo el dueño de la reserva puede pagarla')
        if self.repo.get_reserva_pagada(reserva.id):
            raise ReservaYaPagada()

        pago = Pago(reserva, datos.metodo, reserva.tarifa, ahora)
        pago.estado = procesar(pago, {'numero_tarjeta': datos.numero_tarjeta})
        return self.repo.guardar(pago)

    def confirmar_pago(
        self, usuario: Usuario, pago_id: int, aprobar: bool
    ) -> Pago:
        """El paseador de la reserva aprueba o rechaza el pago."""
        pago = self._obtener(pago_id)
        pago.confirmar(usuario.id, aprobar)
        return self.repo.guardar(pago)

    def obtener_pago(self, usuario: Usuario, pago_id: int) -> Pago:
        pago = self._obtener(pago_id)
        reserva = self.reservas.obtener_por_id(pago.reserva_id)
        es_dueno = reserva is not None and reserva.dueno_id == usuario.id
        if usuario.id != pago.paseador_id and not es_dueno:
            raise NoAutorizado('No tiene permiso para ver este pago')
        return pago

    def _obtener(self, pago_id: int) -> Pago:
        pago = self.repo.get_pago_por_id(pago_id)
        if pago is None:
            raise PagoNoEncontrado()
        return pago
