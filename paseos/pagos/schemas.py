"""Schemas Pydantic de pagos: qué datos entran y salen por la API.

El número de tarjeta entra en PagoCrear solo para validarlo: nunca se guarda ni se devuelve (PagoPublico no lo tiene).
"""

from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from paseos.pagos.enums import EstadoPago, MetodoPago


class CrearPago(BaseModel):
    """Datos para pagar una reserva finalizada."""

    reserva_id: int
    metodo: MetodoPago
    numero_tarjeta: str | None = Field(
        default=None,
        pattern=r'^\d{12,19}$',
        repr=False,
        description='Solo para pagos con tarjeta.',
    )


class ConfirmarPago(BaseModel):
    """El paseador aprueba o rechaza un pago pendiente (solo para efectivo y transferencia)."""

    aprobar: bool


class PagoPublico(BaseModel):
    """Lo que devuelve la API de un pago."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    reserva_id: int | None
    paseador_id: int | None
    metodo: MetodoPago
    monto: Decimal
    estado: EstadoPago
    creado_en: datetime
