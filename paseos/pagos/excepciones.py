"""Errores de negocio del módulo pagos.

Heredan de las clases base de paseos.core.exceptions
"""

from paseos.core.exceptions import (
    Conflicto,
    NoAutorizado,
    NoEncontrado,
    SolicitudInvalida,
)


class PagoInvalidoError(Conflicto):
    """No se puede crear el pago (reserva sin finalizar o monto inválido)."""

    mensaje = 'No se puede crear el pago para esta reserva'


class ConfirmacionInvalidaError(Conflicto):
    """La confirmación manual del pago no está permitida."""

    mensaje = 'No se puede confirmar este pago'


class DatosDePagoInvalidosError(SolicitudInvalida):
    """Los datos del medio de pago son inválidos o faltan."""

    mensaje = 'Los datos del medio de pago son inválidos o faltan'


class PaseadorNoCorrespondeError(NoAutorizado):
    """Quien confirma no es el paseador de la reserva."""

    mensaje = 'Solo el paseador de la reserva puede confirmar el pago'


class PagoNoEncontrado(NoEncontrado):
    """No existe un pago con ese id."""

    mensaje = 'Pago no encontrado'


class ReservaNoEncontrada(NoEncontrado):
    """No existe la reserva que se quiere pagar."""

    mensaje = 'Reserva no encontrada'


class ReservaYaPagada(Conflicto):
    """La reserva ya tiene un pago vigente (pendiente o aprobado)."""

    mensaje = 'La reserva ya tiene un pago pendiente o aprobado'
