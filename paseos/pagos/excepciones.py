"""Errores de negocio del módulo pagos.

Heredan de las clases base de paseos.core.exceptions
"""

from paseos.core.exceptions import Conflicto, SolicitudInvalida


class PagoInvalidoError(Conflicto):
    """No se puede crear el pago (reserva sin finalizar o monto inválido)."""

    mensaje = 'No se puede crear el pago para esta reserva'


class ConfirmacionInvalidaError(Conflicto):
    """La confirmación manual del pago no está permitida."""

    mensaje = 'No se puede confirmar este pago'


class DatosDePagoInvalidosError(SolicitudInvalida):
    """Los datos del medio de pago son inválidos o faltan."""

    mensaje = 'Los datos del medio de pago son inválidos o faltan'