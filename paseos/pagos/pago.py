# pago.py
from datetime import datetime
from decimal import Decimal

from sqlalchemy import Enum, ForeignKey, Numeric
from sqlalchemy.orm import Mapped, mapped_column

from paseos.core.database import Base
from paseos.pagos.enums import EstadoPago, MetodoPago
from paseos.pagos.excepciones import (
    ConfirmacionInvalidaError, 
    PagoInvalidoError,
)
from paseos.reservas.enums import EstadoReserva

# Metodos de pago que se confirman a mano:
METODOS_CON_CONFIRMACION = (MetodoPago.EFECTIVO, MetodoPago.TRANSFERENCIA)


class Pago(Base):
    """
    Pago de un paseo ya finalizado.

    El número de tarjeta no es un atributo: no se guarda.
    Se valida y se descarta.

    paseador_id es una copia del paseador de al reserva al momento de pagar, para poder validas la confirmacion.
    """

    __tablename__ = 'pagos'

    id: Mapped[int] = mapped_column(primary_key=True)
    reserva_id: Mapped[int | None] = mapped_column(ForeignKey('reservas.id'))
    paseador_id: Mapped[int | None] = mapped_column(ForeignKey('usuarios.id'))
    metodo: Mapped[MetodoPago] = mapped_column(Enum(MetodoPago))
    monto: Mapped[Decimal] = mapped_column(Numeric(10,2))
    estado: Mapped[EstadoPago] = mapped_column(Enum(EstadoPago))
    creado_en: Mapped[datetime]

    def __init__(
        self, reserva, metodo: MetodoPago, monto: Decimal, ahora: datetime
    ):
        if reserva.estado != EstadoReserva.FINALIZADA:
            raise PagoInvalidoError(
                'Debe esperar a que finalice el paseo para realizar el pago'
            )
        if monto <= 0:
            raise PagoInvalidoError('El monto debe ser mayor a cero')

        '''
        self.reserva = reserva
        self.metodo = metodo
        self.monto = monto
        self.estado = EstadoPago.PENDIENTE
        self.creado_en = ahora
        '''
        self.reserva_id = reserva.id
        self.paseador_id = reserva.paseador_id
        self.metodo = metodo
        self.monto = monto
        self.estado = EstadoPago.PENDIENTE
        self.creado_en = ahora


    def confirmar(self, paseador_id: int, aprobar: bool) -> None:
        """El paseador aprueba o rechaza el pago pendiente"""

        if self.metodo not in METODOS_CON_CONFIRMACION:
            raise ConfirmacionInvalidaError(
                'Un pago con tarjeta no se confirma a mano'
            )

        if paseador_id != self.paseador_id:
            raise ConfirmacionInvalidaError(
                'Solo el paseador asignado puede confirmar el pago'
            )

        # Un pago APROBADO es definitivo. Uno RECHAZADO puede corregirse
        # (el paseador se pudo equivocar), por eso solo se bloquea APROBADO.

        if self.estado == EstadoPago.APROBADO:
            raise ConfirmacionInvalidaError('El pago ya fue confirmado')

        if aprobar:
            self.estado = EstadoPago.APROBADO
        else:
            self.estado = EstadoPago.RECHAZADO
