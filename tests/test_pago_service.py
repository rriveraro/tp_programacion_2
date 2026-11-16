from datetime import datetime
from decimal import Decimal
from types import SimpleNamespace

import pytest

from config import NUMERO_TARJETA_APROBADA, NUMERO_TARJETA_RECHAZADA
from paseos.core.exceptions import NoAutorizado
from paseos.pagos.enums import EstadoPago, MetodoPago
from paseos.pagos.excepciones import (
    ConfirmacionInvalidaError,
    DatosDePagoInvalidosError,
    PagoInvalidoError,
    PagoNoEncontrado,
    ReservaNoEncontrada,
    ReservaYaPagada,
)
from paseos.pagos.schemas import CrearPago
from paseos.pagos.service import PagoService
from paseos.reservas.enums import EstadoReserva

AHORA = datetime(2026, 11, 13, 15, 0)
RESERVA_ID = 10
DOS = 2
TARIFA = Decimal('8800.00')
DUENO = SimpleNamespace(id=1)
PASEADOR = SimpleNamespace(id=2)
OTRO = SimpleNamespace(id=3)


class RepositorioEnMemoria:
    """Repositorio de mentira: guarda los pagos en una lista."""

    def __init__(self):
        self.pagos = []

    def get_pago_por_id(self, pago_id):
        return next((p for p in self.pagos if p.id == pago_id), None)

    def get_reserva_pagada(self, reserva_id):
        return next(
            (
                p
                for p in self.pagos
                if p.reserva_id == reserva_id
                and p.estado != EstadoPago.RECHAZADO
            ),
            None,
        )

    def guardar(self, pago):
        if pago not in self.pagos:
            pago.id = len(self.pagos) + 1
            self.pagos.append(pago)
        return pago


class ReservasEnMemoria:
    """Reemplaza a ReservaRepository: busca reservas en un diccionario."""

    def __init__(self):
        self.reservas = {RESERVA_ID: reserva()}

    def obtener_por_id(self, reserva_id):
        return self.reservas.get(reserva_id)


def reserva(estado=EstadoReserva.FINALIZADA):
    return SimpleNamespace(
        id=RESERVA_ID,
        estado=estado,
        tarifa=TARIFA,
        paseador_id=PASEADOR.id,
        dueno_id=DUENO.id,
    )


@pytest.fixture
def repo():
    return RepositorioEnMemoria()


@pytest.fixture
def reservas():
    return ReservasEnMemoria()


@pytest.fixture
def service(repo, reservas):
    return PagoService(repo, reservas)


def pedido(
    metodo=MetodoPago.EFECTIVO, numero_tarjeta=None, reserva_id=RESERVA_ID
):
    return CrearPago(
        reserva_id=reserva_id, metodo=metodo, numero_tarjeta=numero_tarjeta
    )


def test_pago_en_efectivo_queda_pendiente_con_la_tarifa(service, repo):
    pago = service.crear_pago(DUENO, pedido(), AHORA)
    assert pago.estado == EstadoPago.PENDIENTE
    assert pago.monto == TARIFA
    assert pago.reserva_id == RESERVA_ID
    assert pago.paseador_id == PASEADOR.id
    assert repo.pagos == [pago]


@pytest.mark.parametrize(
    ('numero', 'estado'),
    [
        (NUMERO_TARJETA_APROBADA, EstadoPago.APROBADO),
        (NUMERO_TARJETA_RECHAZADA, EstadoPago.RECHAZADO),
    ],
)
def test_pago_con_tarjeta_se_resuelve_al_instante(service, numero, estado):
    pago = service.crear_pago(DUENO, pedido(MetodoPago.TARJETA, numero), AHORA)
    assert pago.estado == estado


def test_tarjeta_sin_numero_no_guarda_nada(service, repo):
    with pytest.raises(DatosDePagoInvalidosError):
        service.crear_pago(DUENO, pedido(MetodoPago.TARJETA), AHORA)
    assert repo.pagos == []


def test_el_numero_de_tarjeta_no_se_guarda(service):
    pago = service.crear_pago(
        DUENO, pedido(MetodoPago.TARJETA, NUMERO_TARJETA_APROBADA), AHORA
    )
    assert NUMERO_TARJETA_APROBADA not in str(vars(pago))


def test_reserva_inexistente(service):
    with pytest.raises(ReservaNoEncontrada):
        service.crear_pago(DUENO, pedido(reserva_id=99), AHORA)


@pytest.mark.parametrize('usuario', [PASEADOR, OTRO])
def test_solo_el_dueno_de_la_reserva_puede_pagar(service, usuario):
    with pytest.raises(NoAutorizado):
        service.crear_pago(usuario, pedido(), AHORA)


def test_no_se_paga_una_reserva_sin_finalizar(service, repo, reservas):
    reservas.reservas[RESERVA_ID] = reserva(EstadoReserva.ACEPTADA)
    with pytest.raises(PagoInvalidoError):
        service.crear_pago(DUENO, pedido(), AHORA)
    assert repo.pagos == []


def test_una_reserva_no_se_paga_dos_veces(service):
    service.crear_pago(DUENO, pedido(), AHORA)
    with pytest.raises(ReservaYaPagada):
        service.crear_pago(DUENO, pedido(), AHORA)


def test_tras_un_pago_rechazado_se_puede_reintentar(service, repo):
    service.crear_pago(
        DUENO, pedido(MetodoPago.TARJETA, NUMERO_TARJETA_RECHAZADA), AHORA
    )
    pago = service.crear_pago(
        DUENO, pedido(MetodoPago.TARJETA, NUMERO_TARJETA_APROBADA), AHORA
    )
    assert pago.estado == EstadoPago.APROBADO
    assert len(repo.pagos) == DOS


@pytest.mark.parametrize(
    ('aprobar', 'estado'),
    [(True, EstadoPago.APROBADO), (False, EstadoPago.RECHAZADO)],
)
def test_el_paseador_confirma_o_rechaza(service, aprobar, estado):
    pago = service.crear_pago(DUENO, pedido(), AHORA)
    confirmado = service.confirmar_pago(PASEADOR, pago.id, aprobar)
    assert confirmado.estado == estado


@pytest.mark.parametrize('usuario', [DUENO, OTRO])
def test_solo_el_paseador_de_la_reserva_confirma(service, usuario):
    pago = service.crear_pago(DUENO, pedido(), AHORA)
    with pytest.raises(NoAutorizado):
        service.confirmar_pago(usuario, pago.id, True)
    assert pago.estado == EstadoPago.PENDIENTE


def test_un_pago_aprobado_no_se_puede_cambiar(service):
    pago = service.crear_pago(DUENO, pedido(), AHORA)
    service.confirmar_pago(PASEADOR, pago.id, True)
    with pytest.raises(ConfirmacionInvalidaError):
        service.confirmar_pago(PASEADOR, pago.id, False)


def test_confirmar_un_pago_inexistente(service):
    with pytest.raises(PagoNoEncontrado):
        service.confirmar_pago(PASEADOR, 99, True)


@pytest.mark.parametrize('usuario', [DUENO, PASEADOR])
def test_dueno_y_paseador_pueden_ver_el_pago(service, usuario):
    pago = service.crear_pago(DUENO, pedido(), AHORA)
    assert service.obtener_pago(usuario, pago.id) is pago


def test_un_tercero_no_puede_ver_el_pago(service):
    pago = service.crear_pago(DUENO, pedido(), AHORA)
    with pytest.raises(NoAutorizado):
        service.obtener_pago(OTRO, pago.id)


def test_el_numero_de_tarjeta_no_se_muestra_en_el_schema():
    datos = pedido(MetodoPago.TARJETA, NUMERO_TARJETA_APROBADA)
    assert NUMERO_TARJETA_APROBADA not in repr(datos)