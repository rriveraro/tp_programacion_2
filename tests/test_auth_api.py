from datetime import date
from http import HTTPStatus

from tests.conftest import datos_usuario

PASSWORD = 'clave-segura-123'


def registrar(client, **cambios):
    datos = datos_usuario(**cambios).model_dump(mode='json')
    return client.post('/auth/registro', json=datos)


def login(client, email='ana@mail.com', password=PASSWORD):
    return client.post(
        'auth/login', data={'username': email, 'password': password}
    )


def test_registro_devuelve_el_usuario_sin_contra(client):
    respuesta = registrar(client)
    # verifica que la api respondio 201 created:
    assert respuesta.status_code == HTTPStatus.CREATED
    cuerpo = respuesta.json()
    # verificamos lo que devuelve y no devuelve:
    assert cuerpo['email'] == 'ana@mail.com'
    assert cuerpo['activo'] is True
    assert 'password' not in cuerpo
    assert 'password_hash' not in cuerpo


def test_registro_con_mail_repetido(client):
    registrar(client)
    respuesta = registrar(client, dni='40111222')
    # verificamos que entre en conflicto:
    assert respuesta.status_code == HTTPStatus.CONFLICT


def test_registro_de_un_menor(client):
    fecha_10_anios = date(date.today().year - 10, 1, 1)
    respuesta = registrar(client, fecha_nacimiento=fecha_10_anios)
    assert respuesta.status_code == HTTPStatus.BAD_REQUEST


def test_registro_con_datos_invalidos(client):
    datos = datos_usuario().model_dump(mode='json')
    datos['dni'] = 'abc'
    respuesta = client.post('/auth/registro', json=datos)
    assert respuesta.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


def test_login_con_contra_incorrecta(client):
    registrar(client)
    respuesta = login(client, password='clave-456')
    assert respuesta.status_code == HTTPStatus.UNAUTHORIZED


def test_usuario_dado_de_baja_no_loguea(client):
    registrar(client)
    token = login(client).json()['access_token']
    client.delete('/usuarios/me', headers={'Authorization': f'Bearer {token}'})
    assert login(client).status_code == HTTPStatus.UNAUTHORIZED


def test_cambio_contra(client):
    registrar(client)
    token = login(client).json()['access_token']
    respuesta = client.post(
        'auth/cambiar-password',
        json={
            'password_actual': PASSWORD,
            'password_nueva': 'clave-nueva-456',
        },
        headers={'Authorization': f'Bearer {token}'},
    )
    assert respuesta.status_code == HTTPStatus.NO_CONTENT
    assert (
        login(client).status_code == HTTPStatus.UNAUTHORIZED
    )  # Intenta loguearse con la contraseña vieja. Tiene que fallar con 401.
    nueva = login(client, password='clave-nueva-456')
    assert (
        nueva.status_code == HTTPStatus.OK
    )  # Intenta loguearse con la contra nueva. Tiene que funcionar 200.


def test_cambiar_contra_con_la_actual_incorrecta(client):
    registrar(client)
    token = login(client).json()['access_token']
    respuesta = client.post(
        '/auth/cambiar-password',
        json={
            'password_actual': 'no-es-esta-123',
            'password_nueva': 'clave-nueva-456',
        },
        headers={'Authorization': f'Bearer {token}'},
    )
    assert respuesta.status_code == HTTPStatus.BAD_REQUEST


def test_cambiar_contra_sin_token(client):
    respuesta = client.post(
        '/auth/cambiar-password',
        json={
            'password_actual': PASSWORD,
            'password_nueva': 'clave-nueva-456',
        },
    )
    assert respuesta.status_code == HTTPStatus.UNAUTHORIZED
