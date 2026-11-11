""""
Tests unitarios para security, evalua las funciones crearte_access_token, decode_access_token,
 get_password_token, verify_password. No usan la base de datos: reciben un valor y devuelven otro.
"""

from paseos.core import security
from paseos.core.security import (
    create_access_token,
    decode_access_token,
    get_password_hash,
    verify_password,
)


def test_hash_no_es_la_contrasena_original():
    hash_ = get_password_hash('clave12345')

    assert hash_ != 'clave12345'


def test_verify_password_correcta():
    hash_ = get_password_hash('clave12345')

    assert verify_password('clave12345', hash_) is True


def test_verify_password_incorrecta():
    hash_ = get_password_hash('clave12345')

    assert verify_password('otra-clave', hash_) is False


def test_mismo_password_genera_hashes_distintos():
    assert get_password_hash('clave12345') != get_password_hash('clave12345')


def test_token_conserva_los_datos():
    token = create_access_token({'sub': 'ana@mail.com'})

    datos = decode_access_token(token)

    assert datos['sub'] == 'ana@mail.com'
    assert 'exp' in datos


def test_token_manipulado_devuelve_none():
    token = create_access_token({'sub': 'ana@mail.com'})

    assert decode_access_token(token + 'x') is None


def test_token_basura_devuelve_none():
    assert decode_access_token('no-soy-un-token') is None


def test_token_vencido_devuelve_none(monkeypatch):
    monkeypatch.setattr(security.settings, 'ACCESS_TOKEN_EXPIRE_MINUTES', -1)
    token = create_access_token({'sub': 'ana@mail.com'})

    assert decode_access_token(token) is None