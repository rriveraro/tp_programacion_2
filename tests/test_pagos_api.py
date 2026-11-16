"""Tests de los endpoints /pagos, con la base de prueba y una reserva real."""

from datetime import date, time
from decimal import Decimal
from http import HTTPStatus

import pytest

from config import NUMERO_TARJETA_APROBADA
from paseos.mascotas.enums import Tamaño as Tamano
from paseos.mascotas.models import Mascota
from paseos.reservas.enums import EstadoReserva
from paseos.reservas.reservas import Reserva
from paseos.reservas.turno import Turno
from paseos.usuarios.enums import Barrio, Rol
from tests.conftest import HOY, datos_usuario, headers_de


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
def otro(service):
    return service.crear_usuario(
        datos_usuario(email='otro@mail.com', dni='35111222'),
        password_hash='hash-de-prueba',
        hoy=HOY,
    )


def crear_reserva(db, dueno, paseador, estado=EstadoReserva.FINALIZADA):
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
        tarifa=Decimal('8800.00'),
        comision=Decimal('1320.00'),
        calle='Av. Corrientes',
        numero='1234',
        barrio=Barrio.ALMAGRO,
    )
    reserva.estado = estado
    reserva.paseador_id = paseador.id
    db.add(reserva)
    db.commit()
    return reserva


@pytest.fixture
def reserva(db, dueno, paseador):
    return crear_reserva(db, dueno, paseador)


@pytest.fixture
def pago_id(client, dueno, reserva):
    """Id de un pago en efectivo, pendiente, de la reserva."""
    respuesta = pagar(client, dueno, reserva.id)
    return respuesta.json()['id']


def pagar(client, usuario, reserva_id, metodo='EFECTIVO', numero=None):
    datos = {'reserva_id': reserva_id, 'metodo': metodo}
    if numero is not None:
        datos['numero_tarjeta'] = numero
    return client.post('/pagos', json=datos, headers=headers_de(usuario))


def confirmar(client, usuario, pago_id, aprobar=True):
    return client.post(
        f'/pagos/{pago_id}/confirmar',
        json={'aprobar': aprobar},
        headers=headers_de(usuario),
    )


# --- POST /pagos ------------------------------------------------------


def test_el_dueno_paga_en_efectivo(client, dueno, reserva):
    respuesta = pagar(client, dueno, reserva.id)
    assert respuesta.status_code == HTTPStatus.CREATED
    cuerpo = respuesta.json()
    assert cuerpo['estado'] == 'PENDIENTE'
    assert Decimal(cuerpo['monto']) == Decimal('8800.00')
    assert cuerpo['reserva_id'] == reserva.id


def test_pago_con_tarjeta_aprobada(client, dueno, reserva):
    respuesta = pagar(
        client, dueno, reserva.id, 'TARJETA', NUMERO_TARJETA_APROBADA
    )
    assert respuesta.status_code == HTTPStatus.CREATED
    assert respuesta.json()['estado'] == 'APROBADO'


def test_la_respuesta_no_tiene_el_numero_de_tarjeta(client, dueno, reserva):
    respuesta = pagar(
        client, dueno, reserva.id, 'TARJETA', NUMERO_TARJETA_APROBADA
    )
    assert 'numero_tarjeta' not in respuesta.json()
    assert NUMERO_TARJETA_APROBADA not in respuesta.text


def test_tarjeta_con_letras(client, dueno, reserva):
    respuesta = pagar(client, dueno, reserva.id, 'TARJETA', '4111abc')
    assert respuesta.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


def test_tarjeta_desconocida(client, dueno, reserva):
    respuesta = pagar(client, dueno, reserva.id, 'TARJETA', '1234567890123')
    assert respuesta.status_code == HTTPStatus.BAD_REQUEST


def test_pagar_sin_token(client, reserva):
    respuesta = client.post(
        '/pagos', json={'reserva_id': reserva.id, 'metodo': 'EFECTIVO'}
    )
    assert respuesta.status_code == HTTPStatus.UNAUTHORIZED


def test_solo_el_dueno_puede_pagar(client, paseador, reserva):
    respuesta = pagar(client, paseador, reserva.id)
    assert respuesta.status_code == HTTPStatus.FORBIDDEN


def test_reserva_inexistente(client, dueno):
    respuesta = pagar(client, dueno, 999)
    assert respuesta.status_code == HTTPStatus.NOT_FOUND


def test_reserva_sin_finalizar(client, db, dueno, paseador):
    aceptada = crear_reserva(db, dueno, paseador, EstadoReserva.ACEPTADA)
    respuesta = pagar(client, dueno, aceptada.id)
    assert respuesta.status_code == HTTPStatus.CONFLICT


def test_no_se_paga_dos_veces(client, dueno, reserva):
    pagar(client, dueno, reserva.id)
    respuesta = pagar(client, dueno, reserva.id)
    assert respuesta.status_code == HTTPStatus.CONFLICT


# --- POST /pagos/{id}/confirmar ----------------------------------------


@pytest.mark.parametrize(
    ('aprobar', 'estado'), [(True, 'APROBADO'), (False, 'RECHAZADO')]
)
def test_el_paseador_confirma_o_rechaza(
    client, paseador, pago_id, aprobar, estado
):
    respuesta = confirmar(client, paseador, pago_id, aprobar)
    assert respuesta.status_code == HTTPStatus.OK
    assert respuesta.json()['estado'] == estado


def test_el_dueno_no_puede_confirmar(client, dueno, pago_id):
    respuesta = confirmar(client, dueno, pago_id)
    assert respuesta.status_code == HTTPStatus.FORBIDDEN


def test_un_pago_con_tarjeta_no_se_confirma(client, dueno, paseador, reserva):
    pago_id = pagar(
        client, dueno, reserva.id, 'TARJETA', NUMERO_TARJETA_APROBADA
    ).json()['id']
    respuesta = confirmar(client, paseador, pago_id)
    assert respuesta.status_code == HTTPStatus.CONFLICT


def test_confirmar_un_pago_inexistente(client, paseador):
    respuesta = confirmar(client, paseador, 999)
    assert respuesta.status_code == HTTPStatus.NOT_FOUND


# --- GET /pagos/{id} ----------------------------------------------------


@pytest.mark.parametrize('quien', ['dueno', 'paseador'])
def test_dueno_y_paseador_ven_el_pago(client, request, pago_id, quien):
    usuario = request.getfixturevalue(quien)
    respuesta = client.get(f'/pagos/{pago_id}', headers=headers_de(usuario))
    assert respuesta.status_code == HTTPStatus.OK
    assert respuesta.json()['id'] == pago_id


def test_un_tercero_no_ve_el_pago(client, otro, pago_id):
    respuesta = client.get(f'/pagos/{pago_id}', headers=headers_de(otro))
    assert respuesta.status_code == HTTPStatus.FORBIDDEN


def test_ver_un_pago_inexistente(client, dueno):
    respuesta = client.get('/pagos/999', headers=headers_de(dueno))
    assert respuesta.status_code == HTTPStatus.NOT_FOUND