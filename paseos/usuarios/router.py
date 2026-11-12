"""Endpoints del módulo usuarios.

Todos operan sobre el usuario logueado (/usuarios/me): cada usuario solo
accede a sus propios datos, así que no hace falta recibir un id por URL.
El registro y el login están en el módulo auth.
"""

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from paseos.core.database import get_db
from paseos.core.dependencies import get_usuario_actual
from paseos.usuarios.models import Usuario
from paseos.usuarios.repository import UsuarioRepository
from paseos.usuarios.schemas import UsuarioActualizar, UsuarioPublico
from paseos.usuarios.service import UsuarioService

router = APIRouter(prefix='/usuarios', tags=['usuarios'])


def get_usuario_service(db: Session = Depends(get_db)) -> UsuarioService:
    return UsuarioService(UsuarioRepository(db))


@router.get('/me', response_model=UsuarioPublico)
def ver_mis_datos(usuario: Usuario = Depends(get_usuario_actual)):
    """Devuelve los datos del usuario logueado."""
    return usuario


@router.patch('/me', response_model=UsuarioPublico)
def actualizar_mis_datos(
    cambios: UsuarioActualizar,
    usuario: Usuario = Depends(get_usuario_actual),
    service: UsuarioService = Depends(get_usuario_service),
):
    """Modifica nombre y/o domicilio.

    Email, DNI, rol y fecha de nacimiento no se editan.
    """
    return service.actualizar(usuario, cambios)


@router.delete('/me', status_code=status.HTTP_204_NO_CONTENT)
def darme_de_baja(
    usuario: Usuario = Depends(get_usuario_actual),
    service: UsuarioService = Depends(get_usuario_service),
):
    """Baja lógica. 409 si tiene reservas pendientes o aceptadas."""
    service.dar_de_baja(usuario)
