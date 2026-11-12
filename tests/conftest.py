"""Fixtures compartidas por los tests.

Cada test usa una base SQLite en memoria nueva, así los tests no dependen
unos de otros ni de una base real.
"""

from datetime import date

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from paseos.app import app
from paseos.core.database import Base, get_db
from paseos.core.security import create_access_token
from paseos.usuarios.enums import Barrio, Rol
from paseos.usuarios.repository import UsuarioRepository
from paseos.usuarios.schemas import UsuarioCrear
from paseos.usuarios.service import UsuarioService

HOY = date(
    2026, 11, 8
)  # fecha fija para que los tests de edad no cambien con el tiempo


@pytest.fixture
def db():
    engine = create_engine(
        'sqlite://',
        connect_args={'check_same_thread': False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    sesion = sessionmaker(bind=engine)()
    yield sesion
    sesion.close()
    Base.metadata.drop_all(engine)


@pytest.fixture
def client(db):
    app.dependency_overrides[get_db] = lambda: db
    yield TestClient(app)
    app.dependency_overrides.clear()


@pytest.fixture
def service(db):
    return UsuarioService(UsuarioRepository(db))


def datos_usuario(**cambios) -> UsuarioCrear:
    """Datos válidos de registro; cada test cambia solo lo que le interesa."""
    base = dict(
        email='ana@mail.com',
        password='clave-segura-123',
        nombre='Ana Pérez',
        dni='30111222',
        fecha_nacimiento=date(1990, 5, 20),
        calle='Av. Corrientes',
        numero='1234',
        barrio=Barrio.ALMAGRO,
        rol=Rol.DUENO,
    )
    base.update(cambios)
    return UsuarioCrear(**base)


@pytest.fixture
def dueno(service):
    return service.crear_usuario(
        datos_usuario(), password_hash='hash-de-prueba', hoy=HOY
    )


def headers_de(usuario) -> dict:
    """Header Authorization con un token válido para `usuario`."""
    token = create_access_token({'sub': usuario.email})
    return {'Authorization': f'Bearer {token}'}
