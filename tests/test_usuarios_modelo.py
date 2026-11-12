"""Tests unitarios del modelo Usuario (no usan base de datos)."""

from datetime import date

import pytest

from paseos.usuarios.enums import Barrio, Rol
from paseos.usuarios.exceptions import EdadFueraDeRango
from paseos.usuarios.models import Usuario

HOY = date(2026, 11, 8)


def usuario(rol=Rol.DUENO, nacimiento=date(1990, 5, 20)) -> Usuario:
    return Usuario(
        email='x@mail.com',
        nombre='X',
        dni='12345678',
        fecha_nacimiento=nacimiento,
        calle='Calle',
        numero='1',
        barrio=Barrio.PALERMO,
        password_hash='h',
        rol=rol,
        activo=True,
    )


def test_edad_cuenta_si_ya_cumplio_anios_en_el_anio():
    nacido_hoy_hace_26 = usuario(nacimiento=date(2000, 11, 8))
    cumple_manana_26 = usuario(nacimiento=date(2000, 11, 9))
    edad_cumplida = 26

    assert nacido_hoy_hace_26.edad(HOY) == edad_cumplida
    assert cumple_manana_26.edad(HOY) == edad_cumplida - 1


@pytest.mark.parametrize(
    ('rol', 'nacimiento'),
    [
        (Rol.DUENO, date(2008, 11, 9)),  # 17 años: menor de edad
        (Rol.PASEADOR, date(2008, 11, 9)),  # 17 años
        (
            Rol.PASEADOR,
            date(1960, 11, 8),
        ),  # 66 años: supera el máximo de paseador
        (Rol.DUENO, date(1926, 11, 8)),  # 100 años: supera el máximo de dueño
    ],
)
def test_validar_edad_rechaza_fuera_de_rango(rol, nacimiento):
    with pytest.raises(EdadFueraDeRango):
        usuario(rol=rol, nacimiento=nacimiento).validar_edad(HOY)


@pytest.mark.parametrize(
    ('rol', 'nacimiento'),
    [
        (Rol.DUENO, date(2008, 11, 8)),  # justo 18
        (Rol.PASEADOR, date(1961, 11, 9)),  # justo 65
        (Rol.DUENO, date(1960, 11, 8)),  # 66: un dueño sí puede
        (Rol.DUENO, date(1927, 11, 9)),  # justo 99
    ],
)
def test_validar_edad_acepta_los_limites(rol, nacimiento):
    usuario(rol=rol, nacimiento=nacimiento).validar_edad(HOY)  # no lanza


def test_dar_de_baja_marca_inactivo():
    u = usuario()
    u.dar_de_baja()
    assert u.activo is False


def test_es_dueno_y_es_paseador():
    assert usuario(rol=Rol.DUENO).es_dueno()
    assert not usuario(rol=Rol.DUENO).es_paseador()
    assert usuario(rol=Rol.PASEADOR).es_paseador()
