"""Dependencias de FastAPI compartidas por todos los módulos.

`get_usuario_actual` lee el header `Authorization: Bearer <token>`, lo
decodifica con `security.decode_access_token` y devuelve el Usuario.
Responde 401 si el token es inválido o vencido, o si el usuario fue dado
de baja (un token emitido antes de la baja no debe seguir sirviendo).

El token guarda el email del usuario en "sub" (como en test_security.py).
"""

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from paseos.core.database import get_db
from paseos.core.exceptions import NoAutenticado
from paseos.core.security import decode_access_token
from paseos.usuarios.models import Usuario
from paseos.usuarios.repository import UsuarioRepository

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/auth/login')


def get_usuario_actual(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
) -> Usuario:
    datos = decode_access_token(token)
    if datos is None or 'sub' not in datos:
        raise NoAutenticado('Token inválido o vencido')

    usuario = UsuarioRepository(db).obtener_por_email(datos['sub'])
    if usuario is None or not usuario.activo:
        raise NoAutenticado('Token inválido o vencido')
    return usuario
