"""Endpoint del modulo de pagos.

El router recibe el pedido -> se lo pasa al service -> arma la respuesta.
Las reglas estan en el service y en pago.
"""

from datetime import datetime

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from paseos.core.database import get_db
from paseos.core.dependencies import get_usuario_actual, get_ahora
from paseos.pagos.repository import RepositoryPago
from paseos.pagos.schemas import ConfirmarPago, CrearPago, PagoPublico
from paseos.pagos.service import PagoService
from paseos.reservas.repository import ReservaRepository
from paseos.usuarios.models import Usuario


router = APIRouter(prefix='/pagos', tags=['pagos'])


def get_pago_service(db: Session = Depends(get_db)) -> PagoService:
    return PagoService(RepositoryPago(db), ReservaRepository(db))


@router.post(
    '', response_model=PagoPublico, status_code=status.HTTP_201_CREATED
)
def pagar(
    datos: CrearPago,
    usuario: Usuario = Depends(get_usuario_actual),
    service: PagoService = Depends(get_pago_service),
):
    """El dueño paga una reserva finalizada."""
    return service.crear_pago(usuario, datos, ahora= Depends(get_ahora))


@router.get('/{pago_id}', response_model=PagoPublico)
def ver_pago(
    pago_id: int,
    usuario: Usuario = Depends(get_usuario_actual),
    service: PagoService = Depends(get_pago_service),
):
    return service.obtener_pago(usuario, pago_id)


@router.post('/{pago_id}/confirmar', response_model=PagoPublico)
def confirmar(
    pago_id: int,
    datos: ConfirmarPago,
    usuario: Usuario = Depends(get_usuario_actual),
    service: PagoService = Depends(get_pago_service),
):
    return service.confirmar_pago(usuario, pago_id, datos.aprobar)
