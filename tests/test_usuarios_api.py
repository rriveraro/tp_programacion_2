"""Tests de los endpoints /usuarios/me."""

from datetime import date, time
from decimal import Decimal
from http import HTTPStatus

from paseos.mascotas.enums import Tamaño  # noqa: PLC2403
from paseos.mascotas.models import Mascota
from paseos.reservas.reservas import Reserva
from paseos.reservas.turno import Turno
from tests.conftest import headers_de


def test_sin_token_responde_401(client):
    assert client.get('/usuarios/me').status_code == HTTPStatus.UNAUTHORIZED


def test_ver_mis_datos_no_expone_la_contrasena(client, dueno):
    respuesta = client.get('/usuarios/me', headers=headers_de(dueno))
    assert respuesta.status_code == HTTPStatus.OK
    cuerpo = respuesta.json()
    assert cuerpo['email'] == 'ana@mail.com'
    assert 'password_hash' not in cuerpo
    assert 'password' not in cuerpo


def test_actualizar_domicilio(client, dueno):
    respuesta = client.patch(
        '/usuarios/me',
        json={
            'calle': 'Av. Rivadavia',
            'numero': '5000',
            'barrio': 'CABALLITO',
        },
        headers=headers_de(dueno),
    )
    assert respuesta.status_code == HTTPStatus.OK
    assert respuesta.json()['barrio'] == 'CABALLITO'
    assert respuesta.json()['nombre'] == 'Ana Pérez'  # lo no enviado no cambia


def test_no_se_puede_cambiar_el_rol(client, dueno):
    respuesta = client.patch(
        '/usuarios/me', json={'rol': 'PASEADOR'}, headers=headers_de(dueno)
    )
    assert respuesta.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


def test_barrio_inexistente_responde_422(client, dueno):
    respuesta = client.patch(
        '/usuarios/me', json={'barrio': 'GOTHAM'}, headers=headers_de(dueno)
    )
    assert respuesta.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


def test_actualizar_sin_datos_responde_400(client, dueno):
    respuesta = client.patch(
        '/usuarios/me', json={}, headers=headers_de(dueno)
    )
    assert respuesta.status_code == HTTPStatus.BAD_REQUEST


def test_baja_y_el_token_deja_de_servir(client, dueno):
    headers = headers_de(dueno)
    assert (
        client.delete('/usuarios/me', headers=headers).status_code
        == HTTPStatus.NO_CONTENT
    )
    assert (
        client.get('/usuarios/me', headers=headers).status_code
        == HTTPStatus.UNAUTHORIZED
    )


def test_baja_rechazada_si_tiene_una_reserva_pendiente(client, db, dueno):
    """Prueba la conexión real con reservas (sin verificador falso)."""
    mascota = Mascota(
        dueno_id=dueno.id,
        nombre='Firulais',
        fecha_nacimiento=date(2020, 1, 1),
        tamaño=Tamaño.MEDIANO,
        raza='Mestizo',
    )
    db.add(mascota)
    db.commit()
    reserva = Reserva(
        mascota_id=mascota.id,
        turno=Turno(date(2026, 12, 1), time(10), time(11)),
        tarifa=Decimal('9600'),
        comision=Decimal('1440'),
        calle=dueno.calle,
        numero=dueno.numero,
        barrio=dueno.barrio,
    )
    db.add(reserva)
    db.commit()

    headers = headers_de(dueno)
    respuesta = client.delete('/usuarios/me', headers=headers)

    assert respuesta.status_code == HTTPStatus.CONFLICT
    assert client.get('/usuarios/me', headers=headers).status_code == (
        HTTPStatus.OK
    )
