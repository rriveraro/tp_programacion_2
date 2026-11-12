"""Tests del servicio de usuarios (con base de datos en memoria)."""

from datetime import date

import pytest

from paseos.usuarios.exceptions import (
    DniYaRegistrado,
    EdadFueraDeRango,
    EmailYaRegistrado,
    UsuarioConReservasActivas,
)
from paseos.usuarios.repository import UsuarioRepository
from paseos.usuarios.service import UsuarioService
from tests.conftest import HOY, datos_usuario


def test_crear_usuario_guarda_hash_y_queda_activo(service):
    u = service.crear_usuario(
        datos_usuario(email='ANA@Mail.com'), 'hash-x', HOY
    )
    assert u.id is not None
    assert u.email == 'ana@mail.com'  # se normaliza en minúscula
    assert u.password_hash == 'hash-x'
    assert u.activo is True


def test_no_permite_email_repetido(service, dueno):
    with pytest.raises(EmailYaRegistrado):
        service.crear_usuario(datos_usuario(dni='99999999'), 'h', HOY)


def test_no_permite_dni_repetido(service, dueno):
    with pytest.raises(DniYaRegistrado):
        service.crear_usuario(datos_usuario(email='otra@mail.com'), 'h', HOY)


def test_edad_invalida_no_guarda_nada(service):
    with pytest.raises(EdadFueraDeRango):
        service.crear_usuario(
            datos_usuario(fecha_nacimiento=date(2010, 1, 1)), 'h', HOY
        )
    assert service.repo.obtener_por_email('ana@mail.com') is None


def test_baja_rechazada_si_tiene_reservas_activas(db, dueno):
    service = UsuarioService(
        UsuarioRepository(db), tiene_reservas_activas=lambda u: True
    )
    with pytest.raises(UsuarioConReservasActivas):
        service.dar_de_baja(dueno)
    assert dueno.activo is True


def test_usuario_dado_de_baja_no_puede_loguearse(service, dueno):
    service.dar_de_baja(dueno)
    assert service.obtener_activo_por_email('ana@mail.com') is None
