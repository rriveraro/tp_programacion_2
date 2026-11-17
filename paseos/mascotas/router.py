from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from paseos.core.database import get_db
from paseos.core.dependencies import get_usuario_actual
from paseos.mascotas.repository import MascotaRepository
from paseos.mascotas.schemas import (
    MascotaActualizar,
    MascotaCrear,
    MascotaPublica,
)
from paseos.mascotas.service import MascotaService
from paseos.reservas.repository import ReservaRepository
from paseos.usuarios.models import Usuario

router = APIRouter(
    prefix="/mascotas",
    tags=["Mascotas"],
)


def get_mascota_service(db: Session = Depends(get_db)) -> MascotaService:
    return MascotaService(
        repo=MascotaRepository(db),
        reserva_repo=ReservaRepository(db),
    )


@router.post(
    "",
    response_model=MascotaPublica,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar una nueva mascota",
)
def crear_mascota(
    datos: MascotaCrear,
    usuario: Usuario = Depends(get_usuario_actual),
    service: MascotaService = Depends(get_mascota_service),
):
    return service.registrar_mascota(dueno=usuario, datos=datos)


@router.get(
    "",
    response_model=list[MascotaPublica],
    status_code=status.HTTP_200_OK,
    summary="Listar las mascotas del dueño autenticado",
)
def listar_mis_mascotas(
    usuario: Usuario = Depends(get_usuario_actual),
    service: MascotaService = Depends(get_mascota_service),
):
    return service.listar_mis_mascotas(dueno=usuario)


@router.get(
    "/{id}",
    response_model=MascotaPublica,
    status_code=status.HTTP_200_OK,
    summary="Obtener detalle de una mascota",
)
def obtener_mascota(
    id: int,
    usuario: Usuario = Depends(get_usuario_actual),
    service: MascotaService = Depends(get_mascota_service),
):
    return service.obtener_mascota(mascota_id=id, dueno=usuario)


@router.patch(
    "/{id}",
    response_model=MascotaPublica,
    status_code=status.HTTP_200_OK,
    summary="Actualizar datos o vacuna antirrábica de una mascota",
)
def actualizar_mascota(
    id: int,
    datos: MascotaActualizar,
    usuario: Usuario = Depends(get_usuario_actual),
    service: MascotaService = Depends(get_mascota_service),
):
    return service.actualizar_mascota(mascota_id=id, dueno=usuario, datos=datos)


@router.delete(
    "/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar una mascota",
)
def eliminar_mascota(
    id: int,
    usuario: Usuario = Depends(get_usuario_actual),
    service: MascotaService = Depends(get_mascota_service),
):
    service.eliminar_mascota(mascota_id=id, dueno=usuario)
