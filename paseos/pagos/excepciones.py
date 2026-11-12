# Excepciones PAGOS
# ---------------------------------------------------
class PagoError(Exception):
    """Base de las excepciones del modulo de pagos"""


class PagoInvalidoError(PagoError):
    """No se puede crear el pago (La reserva o el monto no son validos)"""


class ConfirmacionInvalidaError(PagoError):
    """La confirmación manual del pago no esta permitida"""


class DatosDePagoInvalidosError(PagoError):
    """Los datos del medio de pago son invalidos o faltan"""
