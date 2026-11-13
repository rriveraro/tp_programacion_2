# test_pago.py
from datetime import date, datetime, time
from decimal import Decimal

import pytest

from config import NUMERO_TARJETA_APROBADA, NUMERO_TARJETA_RECHAZADA
from paseos.pagos.enums import EstadoPago, MetodoPago
from paseos.reservas.enums import EstadoReserva
from paseos.pagos.excepciones import (
    ConfirmacionInvalidaError,
    DatosDePagoInvalidosError,
    PagoInvalidoError,
)
from paseos.pagos.pago import Pago
from paseos.pagos.procesadores import PROCESADORES, procesar
from paseos.reservas.reserva import Reserva
from paseos.reservas.turno import Turno

AHORA = datetime(2026, 11, 10, 15, 0)
TURNO = Turno(date(2026, 11, 10), time(13, 0), time(14, 0))
PASEADOR = 7
MONTO = Decimal('5000')


def reserva_en(estado, paseador_id=PASEADOR):
    """Arma una reserva."""
    reserva = Reserva(mascota_id=1, turno=TURNO)
    reserva.estado = estado
    reserva.paseador_id = paseador_id
    return reserva


def pago_de(metodo):
    return Pago(reserva_en(EstadoReserva.FINALIZADA), metodo, MONTO, AHORA)


def test_pago_nace_pendiente():
    pago = pago_de(MetodoPago.EFECTIVO)
    assert pago.estado == EstadoPago.PENDIENTE
    assert pago.monto == MONTO
    assert pago.creado_en == AHORA


@pytest.mark.parametrize(
    'estado',
    [
        EstadoReserva.PENDIENTE,
        EstadoReserva.ACEPTADA,
        EstadoReserva.CANCELADA,
        EstadoReserva.EXPIRADA,
    ],
)
def test_solo_se_paga_una_reserva_finalizada(estado):
    with pytest.raises(PagoInvalidoError):
        Pago(reserva_en(estado), MetodoPago.EFECTIVO, MONTO, AHORA)


@pytest.mark.parametrize('monto', [Decimal('0'), Decimal('-100')])
def test_monto_debe_ser_positivo(monto):
    reserva = reserva_en(EstadoReserva.FINALIZADA)
    with pytest.raises(PagoInvalidoError):
        Pago(reserva, MetodoPago.EFECTIVO, monto, AHORA)


def test_hay_un_procesador_por_cada_metodo_de_pago():
    assert set(PROCESADORES) == set(MetodoPago)


@pytest.mark.parametrize('metodo', [MetodoPago.EFECTIVO, MetodoPago.TRANSFERENCIA])
def test_efectivo_y_transferencia_quedan_pendientes(metodo):
    assert procesar(pago_de(metodo)) == EstadoPago.PENDIENTE


@pytest.mark.parametrize(
    ('numero', 'esperado'),
    [
        (NUMERO_TARJETA_APROBADA, EstadoPago.APROBADO),
        (NUMERO_TARJETA_RECHAZADA, EstadoPago.RECHAZADO),
    ],
)
def test_tarjeta_de_prueba(numero, esperado):
    pago = pago_de(MetodoPago.TARJETA)
    assert procesar(pago, {'numero_tarjeta': numero}) == esperado


@pytest.mark.parametrize('datos', [None, {}, {'numero_tarjeta': '1234'}])
def test_tarjeta_con_datos_invalidos_lanza_error(datos):
    with pytest.raises(DatosDePagoInvalidosError):
        procesar(pago_de(MetodoPago.TARJETA), datos)


@pytest.mark.parametrize( ('metodo', 'aprobar', 'esperado'), [(MetodoPago.EFECTIVO, True, EstadoPago.APROBADO), (MetodoPago.EFECTIVO, False, EstadoPago.RECHAZADO), (MetodoPago.TRANSFERENCIA, True, EstadoPago.APROBADO), (MetodoPago.TRANSFERENCIA, False, EstadoPago.RECHAZADO), ], )
def test_paseador_confirma_o_rechaza(metodo, aprobar, esperado):
    pago = pago_de(metodo)
    pago.confirmar(PASEADOR, aprobar)
    assert pago.estado == esperado


def test_pago_con_tarjeta_no_se_confirma_a_mano():
    with pytest.raises(ConfirmacionInvalidaError):
        pago_de(MetodoPago.TARJETA).confirmar(PASEADOR, True)


def test_otro_paseador_no_puede_confirmar():
    pago = pago_de(MetodoPago.EFECTIVO)
    with pytest.raises(ConfirmacionInvalidaError):
        pago.confirmar(PASEADOR + 1, True)
    assert pago.estado == EstadoPago.PENDIENTE


def test_pago_rechazado_puede_corregirse_y_aprobarse():
    pago = pago_de(MetodoPago.EFECTIVO)
    pago.confirmar(PASEADOR, False)
    pago.confirmar(PASEADOR, True)
    assert pago.estado == EstadoPago.APROBADO


def test_pago_aprobado_no_puede_cambiar():
    pago = pago_de(MetodoPago.EFECTIVO)
    pago.confirmar(PASEADOR, True)
    with pytest.raises(ConfirmacionInvalidaError):
        pago.confirmar(PASEADOR, False)
    assert pago.estado == EstadoPago.APROBADO