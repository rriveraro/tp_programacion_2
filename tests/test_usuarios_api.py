"""Tests de los endpoints /usuarios/me."""

from http import HTTPStatus

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
