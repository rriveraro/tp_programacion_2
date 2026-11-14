"""Endpoints: registro, login y cambio de contra.
"""

from datetime import date

from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from paseos.auth.schemas import CambiarPassword, Token
from paseos.auth.service import AuthService
from paseos.core.database import get_db
from paseos.core.dependencies import get_usuario_actual
from paseos.usuarios.models import Usuario
from paseos.usuarios.repository import UsuarioRepository
from paseos.usuarios.schemas import UsuarioCrear, UsuarioPublico
from paseos.usuarios.service import UsuarioService

router = APIRouter(prefix='/auth', tags=['auth'])


def get_auth_service(db: Session = Depends(get_db)) -> AuthService:
    return AuthService(UsuarioService(UsuarioRepository(db)))

@router.post(
    '/registro',
    responde_model=UsuarioPublico,
    status_code=status.HTTP_201_CREATED
)
def registrarse(
    datos: UsuarioCrear, service: AuthService = Depends(get_auth_service)
):
    '''Crea un dueño o paseador. 409 si mail o dni ya existen.'''
    return service.registrar(datos, hoy=date.today())

@router.post('/login', response_model=Token)
def login(
    formulario: OAuth2PasswordRequestForm = Depends(),
    service: AuthService = Depends(get_auth_service)
):
    '''Da token de acceso. 401 si mail o contra fallan.'''
    token = service.login(formulario.username, formulario.password)
    return Token(access_token=token, token_type='bearer')


@router.post('/cambiar-password', status_code=status.HTTP_204_NO_CONTENT)
def cambiar_password(
    datos: CambiarPassword,
    usuario: Usuario = Depends(get_usuario_actual),
    service: AuthService = Depends(get_auth_service)
):
    '''Cambia la contra del usuario logeado.'''
    service.cambiar_password(
        usuario, datos.password_actual, datos.password_nueva
    )