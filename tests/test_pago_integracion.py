"""Pagos con la base de datos y una reserva real (sin simulaciones)."""

from datetime import date, datetime, time
from decimal import Decimal

import pytest

from config import NUMERO_TARJETA_APROBADA, NUMERO_TARJETA_RECHAZADA
from paseos.mascotas.enums import Tamaño as Tamano
from paseos.mascotas.models import Mascota
from paseos.pagos.enums import EstadoPago, MetodoPago
from paseos.pagos.excepciones import ReservaYaPagada
from paseos.pagos.repository import RepositoryPago
from paseos.pagos.schemas import CrearPago
from paseos.pagos.service import PagoService
from paseos.reservas.enums import EstadoReserva
from paseos.reservas.repository import ReservaRepository
from paseos.reservas.reservas import Reserva
from paseos.reservas.turno import Turno
from paseos.usuarios.enums import Barrio, Rol
from tests.conftest import HOY, datos_usuario

AHORA = datetime(2026, 11, 20, 12, 0)
TARIFA = Decimal('8800.00')


@pytest.fixture
def paseador(service):
    return service.crear_usuario(
        datos_usuario(
            email='pasea@mail.com', dni='28111222', rol=Rol.PASEADOR
        ),
        password_hash='hash-de-prueba',
        hoy=HOY,
    )


@pytest.fixture
def reserva(db, dueno, paseador):
    mascota = Mascota(
        dueno_id=dueno.id,
        nombre='Firulais',
        fecha_nacimiento=date(2022, 1, 1),
        tamaño=Tamano.PEQUEÑO,
        raza='Mestizo',
    )
    db.add(mascota)
    db.commit()
    reserva = Reserva(
        mascota_id=mascota.id,
        turno=Turno(date(2026, 11, 20), time(10, 0), time(11, 0)),
        tarifa=TARIFA,
        comision=Decimal('1320.00'),
        calle='Av. Corrientes',
        numero='1234',
        barrio=Barrio.ALMAGRO,
    )
    reserva.estado = EstadoReserva.FINALIZADA
    reserva.paseador_id = paseador.id
    db.add(reserva)
    db.commit()
    return reserva


@pytest.fixture
def pagos(db):
    return PagoService(RepositoryPago(db), ReservaRepository(db))


def pedido(reserva, metodo=MetodoPago.EFECTIVO, numero_tarjeta=None):
    return CrearPago(
        reserva_id=reserva.id, metodo=metodo, numero_tarjeta=numero_tarjeta
    )


def test_la_reserva_conoce_a_su_dueno(reserva, dueno):
    assert reserva.dueno_id == dueno.id


def test_el_dueno_paga_y_el_pago_queda_guardado(db, pagos, reserva, dueno):
    pago = pagos.crear_pago(dueno, pedido(reserva), AHORA)
    guardado = RepositoryPago(db).get_pago_por_id(pago.id)
    assert guardado.monto == TARIFA
    assert guardado.estado == EstadoPago.PENDIENTE
    assert guardado.reserva_id == reserva.id
    assert guardado.paseador_id == reserva.paseador_id


def test_el_paseador_confirma_y_queda_guardado(
    db, pagos, reserva, dueno, paseador
):
    pago = pagos.crear_pago(dueno, pedido(reserva), AHORA)
    pagos.confirmar_pago(paseador, pago.id, aprobar=True)
    db.expire_all()
    assert RepositoryPago(db).get_pago_por_id(pago.id).estado == (
        EstadoPago.APROBADO
    )


def test_no_se_paga_dos_veces_pero_si_tras_un_rechazo(pagos, reserva, dueno):
    rechazado = pagos.crear_pago(
        dueno,
        pedido(reserva, MetodoPago.TARJETA, NUMERO_TARJETA_RECHAZADA),
        AHORA,
    )
    assert rechazado.estado == EstadoPago.RECHAZADO

    aprobado = pagos.crear_pago(
        dueno,
        pedido(reserva, MetodoPago.TARJETA, NUMERO_TARJETA_APROBADA),
        AHORA,
    )
    assert aprobado.estado == EstadoPago.APROBADO

    with pytest.raises(ReservaYaPagada):
        pagos.crear_pago(dueno, pedido(reserva), AHORA)
