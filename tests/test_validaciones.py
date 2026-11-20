import pytest
from pydantic import TypeAdapter, ValidationError

from paseos.core.validaciones import Nombre
from paseos.mascotas.schemas import MascotaActualizar, MascotaCrear
from paseos.usuarios.schemas import UsuarioCrear

NOMBRES_VALIDOS = [
    'María José',
    "D'Angelo",
    'D’Angelo',
    'Ana-Laura',
    'Nuñez',
    'Ana María Núñez',
]
NOMBRES_INVALIDOS = ['1234', 'Ana2', '--', "'Ana", 'Ana-', "''", '   ']


def _usuario(**cambios):
    datos = {
        'email': 'ana@mail.com',
        'password': 'clave-larga-123',
        'nombre': 'Ana',
        'dni': '30111222',
        'fecha_nacimiento': '1990-01-01',
        'calle': 'Corrientes',
        'numero': '123',
        'barrio': 'PALERMO',
        'rol': 'DUENO',
    }
    return UsuarioCrear(**{**datos, **cambios})


def _mascota(**cambios):
    datos = {
        'nombre': 'Fido',
        'fecha_nacimiento': '2020-01-01',
        'tamaño': 'GRANDE',
        'raza': 'Mestizo',
    }
    return MascotaCrear(**{**datos, **cambios})


@pytest.mark.parametrize('nombre', NOMBRES_VALIDOS)
def test_nombre_valido(nombre):
    assert TypeAdapter(Nombre).validate_python(nombre) == nombre


@pytest.mark.parametrize('nombre', NOMBRES_INVALIDOS)
def test_nombre_invalido(nombre):
    with pytest.raises(ValidationError):
        TypeAdapter(Nombre).validate_python(nombre)


def test_nombre_recorta_espacios_de_los_bordes():
    assert TypeAdapter(Nombre).validate_python('  Ana  ') == 'Ana'


@pytest.mark.parametrize('nombre', ['1234', 'A', 'Ana2'])
def test_usuario_rechaza_nombre_invalido(nombre):
    with pytest.raises(ValidationError):
        _usuario(nombre=nombre)


def test_usuario_acepta_nombre_con_tilde():
    assert _usuario(nombre='María José').nombre == 'María José'


@pytest.mark.parametrize(
    'dni', ['01234567', '0123456', '123456', '123456789', '12a45678']
)
def test_usuario_rechaza_dni_invalido(dni):
    with pytest.raises(ValidationError):
        _usuario(dni=dni)


@pytest.mark.parametrize('dni', ['1234567', '12345678'])
def test_usuario_acepta_dni_valido(dni):
    assert _usuario(dni=dni).dni == dni


@pytest.mark.parametrize('raza', ['1234', 'Caniche3', '--'])
def test_mascota_rechaza_raza_invalida(raza):
    with pytest.raises(ValidationError):
        _mascota(raza=raza)


def test_mascota_acepta_raza_valida():
    assert _mascota(raza='Ovejero Alemán').raza == 'Ovejero Alemán'


def test_mascota_acepta_nombre_libre():
    assert _mascota(nombre='R2-D2').nombre == 'R2-D2'


def test_mascota_actualizar_valida_la_raza_si_viene():
    with pytest.raises(ValidationError):
        MascotaActualizar(raza='1234')
    assert MascotaActualizar().raza is None