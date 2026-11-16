from datetime import datetime

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from paseos.core.database import get_db
from paseos.core.dependencies import get_ahora, get_usuario_actual
from paseos.mascotas.repository import MascotaRepository
from paseos.reservas.repository import ReservaRepository
from paseos.reservas.schemas import (
    PenalidadSalida,
    ReservaCrear,
    ReservaDetalleDueno,
    ReservaDomicilio,
    ReservaPublica,
)
from paseos.reservas.service import ReservaService
from paseos.usuarios.enums import Barrio, Rol
from paseos.usuarios.models import Usuario

router = APIRouter(
    prefix="/reservas",
    tags=["Reservas"],
)


def get_reserva_service(db: Session = Depends(get_db)) -> ReservaService:
    """Construye el servicio de reservas con sus repositorios."""
    return ReservaService(
        repo=ReservaRepository(db),
        mascota_repo=MascotaRepository(db),
    )


@router.post(
    "",
    response_model=ReservaDetalleDueno,
    status_code=status.HTTP_201_CREATED,
    summary="Crear una nueva reserva de paseo",
)
def crear_reserva(
    datos: ReservaCrear,
    usuario: Usuario = Depends(get_usuario_actual),
    service: ReservaService = Depends(get_reserva_service),
    ahora: datetime = Depends(get_ahora),
):
    """crea una reserva en estado PENDIENTE para una mascota del dueño autenticado."""
    return service.crear_reserva(dueno=usuario, datos=datos, ahora=ahora)


@router.get(
    "/pendientes",
    response_model=list[ReservaPublica],
    status_code=status.HTTP_200_OK,
    summary="Listar reservas pendientes disponibles",
)
def listar_reservas_pendientes(
    barrio: Barrio | None = Query(default=None, description="Filtrar por barrio"),
    usuario: Usuario = Depends(get_usuario_actual),
    service: ReservaService = Depends(get_reserva_service),
    ahora: datetime = Depends(get_ahora),
):
    """Lista las reservas pendientes disponibles para un paseador (sin exponer calle ni número)."""
    return service.listar_pendientes(paseador=usuario, barrio=barrio, ahora=ahora)


@router.get(
    "/mias",
    response_model=list[ReservaDetalleDueno | ReservaPublica],
    status_code=status.HTTP_200_OK,
    summary="Listar reservas del usuario autenticado",
)
def listar_mis_reservas(
    solo_activas: bool = Query(
        default=False, description="Filtrar solo reservas PENDIENTE o ACEPTADA"
    ),
    usuario: Usuario = Depends(get_usuario_actual),
    service: ReservaService = Depends(get_reserva_service),
    ahora: datetime = Depends(get_ahora),
):
    """Devuelve las reservas propias adaptando los campos visibles según el rol (DUENO o PASEADOR)."""
    reservas = service.listar_mis_reservas(
        usuario=usuario, solo_activas=solo_activas, ahora=ahora
    )
    if usuario.rol == Rol.DUENO:
        return [ReservaDetalleDueno.model_validate(r) for r in reservas]
    return [ReservaPublica.model_validate(r) for r in reservas]


@router.get(
    "/penalidades/mias",
    response_model=list[PenalidadSalida],
    status_code=status.HTTP_200_OK,
    summary="Listar penalidades del usuario autenticado",
)
def listar_mis_penalidades(
    usuario: Usuario = Depends(get_usuario_actual),
    service: ReservaService = Depends(get_reserva_service),
    ahora: datetime = Depends(get_ahora),
):
    return service.listar_mis_penalidades(usuario=usuario, ahora=ahora)


@router.get(
    "/{id}/domicilio",
    response_model=ReservaDomicilio,
    status_code=status.HTTP_200_OK,
    summary="Obtener domicilio completo de una reserva aceptada",
)
def obtener_domicilio_reserva(
    id: int,
    usuario: Usuario = Depends(get_usuario_actual),
    service: ReservaService = Depends(get_reserva_service),
    ahora: datetime = Depends(get_ahora),
):
    """Devuelve calle, número y barrio al paseador asignado mientras la reserva esté ACEPTADA."""
    return service.obtener_domicilio(reserva_id=id, paseador=usuario, ahora=ahora)


@router.post(
    "/{id}/aceptar",
    response_model=ReservaPublica,
    status_code=status.HTTP_200_OK,
    summary="Aceptar una reserva pendiente",
)
def aceptar_reserva(
    id: int,
    usuario: Usuario = Depends(get_usuario_actual),
    service: ReservaService = Depends(get_reserva_service),
    ahora: datetime = Depends(get_ahora),
):
    """Asigna al paseador autenticado una reserva que se encuentra PENDIENTE."""
    return service.aceptar_reserva(reserva_id=id, paseador=usuario, ahora=ahora)


@router.post(
    "/{id}/cancelar",
    response_model=ReservaDetalleDueno,
    status_code=status.HTTP_200_OK,
    summary="Cancelar una reserva (dueño)",
)
def cancelar_reserva(
    id: int,
    usuario: Usuario = Depends(get_usuario_actual),
    service: ReservaService = Depends(get_reserva_service),
    ahora: datetime = Depends(get_ahora),
):
    """Permite al dueño de la mascota cancelar su reserva."""
    return service.cancelar_por_dueno(reserva_id=id, dueno=usuario, ahora=ahora)


@router.post(
    "/{id}/retirar-aceptacion",
    response_model=ReservaPublica,
    status_code=status.HTTP_200_OK,
    summary="Retirar aceptación de una reserva (paseador)",
)
def retirar_aceptacion_reserva(
    id: int,
    usuario: Usuario = Depends(get_usuario_actual),
    service: ReservaService = Depends(get_reserva_service),
    ahora: datetime = Depends(get_ahora),
):
    """Permite al paseador asignado retirar su aceptación para que la reserva vuelva a PENDIENTE."""
    return service.cancelar_aceptacion(reserva_id=id, paseador=usuario, ahora=ahora)


@router.post(
    "/{id}/finalizar",
    response_model=ReservaPublica,
    status_code=status.HTTP_200_OK,
    summary="Finalizar una reserva aceptada",
)
def finalizar_reserva(
    id: int,
    usuario: Usuario = Depends(get_usuario_actual),
    service: ReservaService = Depends(get_reserva_service),
    ahora: datetime = Depends(get_ahora),
):
    """Marca el paseo como finalizado al devolver la mascota."""
    return service.finalizar_reserva(reserva_id=id, paseador=usuario, ahora=ahora)