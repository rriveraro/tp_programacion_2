# test_reserva.py
from datetime import date, datetime, time

import pytest

from enums import EstadoReserva
from excepciones import TransicionInvalidaError
from reserva import Reserva
from turno import Turno

AHORA = datetime(2026, 11, 8, 12, 0)
TURNO = Turno(date(2026, 11, 10), time(13, 0), time(14, 0))


def reserva_en(estado, paseador_id=None):
    """arma una reserva ya en el estado pedido (el estado es un enum que se persiste)."""
    reserva = Reserva(mascota_id=1, turno=TURNO)
    reserva.estado = estado
    reserva.paseador_id = paseador_id
    return reserva


def test_reserva_nace_pendiente_sin_paseador():
    reserva = Reserva(mascota_id=1, turno=TURNO)
    assert reserva.estado == EstadoReserva.PENDIENTE
    assert reserva.paseador_id is None


@pytest.mark.parametrize("estado", [EstadoReserva.PENDIENTE, EstadoReserva.ACEPTADA])
def test_dueno_cancela_reserva_activa(estado):
    reserva = reserva_en(estado)
    reserva.cancelar_por_dueno(AHORA)
    assert reserva.estado == EstadoReserva.CANCELADA


def test_paseador_retira_aceptacion_y_vuelve_a_pendiente():
    reserva = reserva_en(EstadoReserva.ACEPTADA, paseador_id=7)
    reserva.cancelar_aceptacion(AHORA)
    assert reserva.estado == EstadoReserva.PENDIENTE
    assert reserva.paseador_id is None


def test_finalizar_a_tiempo():
    reserva = reserva_en(EstadoReserva.ACEPTADA, paseador_id=7)
    ahora = datetime(2026, 11, 10, 13, 50)
    reserva.finalizar(ahora)
    assert reserva.estado == EstadoReserva.FINALIZADA
    assert reserva.devuelta_en == ahora
    assert reserva.devolucion_tardia is False


def test_finalizar_tarde_marca_devolucion_tardia():
    reserva = reserva_en(EstadoReserva.ACEPTADA, paseador_id=7)
    reserva.finalizar(datetime(2026, 11, 10, 14, 30))
    assert reserva.devolucion_tardia is True


def test_expirar_antes_del_limite_lanza_error():
    reserva = reserva_en(EstadoReserva.PENDIENTE)
    with pytest.raises(TransicionInvalidaError):
        reserva.expirar(AHORA)


def test_expirar_pasado_el_limite():
    reserva = reserva_en(EstadoReserva.PENDIENTE)
    reserva.expirar(datetime(2026, 11, 10, 12, 31))
    assert reserva.estado == EstadoReserva.EXPIRADA


@pytest.mark.parametrize(
    "estado",
    [EstadoReserva.CANCELADA, EstadoReserva.EXPIRADA, EstadoReserva.FINALIZADA],
)
def test_estados_finales_no_permiten_acciones(estado):
    reserva = reserva_en(estado)
    with pytest.raises(TransicionInvalidaError):
        reserva.cancelar_por_dueno(AHORA)
    with pytest.raises(TransicionInvalidaError):
        reserva.finalizar(AHORA)


def test_no_se_puede_finalizar_una_reserva_pendiente():
    with pytest.raises(TransicionInvalidaError):
        reserva_en(EstadoReserva.PENDIENTE).finalizar(AHORA)


def test_cancelacion_tardia():
    reserva = reserva_en(EstadoReserva.ACEPTADA, paseador_id=7)
    assert reserva.es_cancelacion_tardia(AHORA) is False
    assert reserva.es_cancelacion_tardia(datetime(2026, 11, 10, 12, 45)) is True
def test_aceptar_reserva_pendiente():
    reserva = reserva_en(EstadoReserva.PENDIENTE)
    reserva.aceptar(7, AHORA)
    assert reserva.estado == EstadoReserva.ACEPTADA
    assert reserva.paseador_id == 7


def test_aceptar_reserva_vencida_lanza_error_y_no_cambia_nada():
    reserva = reserva_en(EstadoReserva.PENDIENTE)
    with pytest.raises(TransicionInvalidaError):
        reserva.aceptar(7, datetime(2026, 11, 10, 12, 31))
    assert reserva.estado == EstadoReserva.PENDIENTE
    assert reserva.paseador_id is None


def test_aceptar_justo_en_el_limite_ya_esta_vencida():
    reserva = reserva_en(EstadoReserva.PENDIENTE)
    with pytest.raises(TransicionInvalidaError):
        reserva.aceptar(7, datetime(2026, 11, 10, 12, 30))


def test_aceptar_reserva_cancelada_lanza_error():
    reserva = reserva_en(EstadoReserva.CANCELADA)
    with pytest.raises(TransicionInvalidaError):
        reserva.aceptar(7, AHORA)