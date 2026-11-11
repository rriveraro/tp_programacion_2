from config import NUMERO_TARJETA_APROBADA, NUMERO_TARJETA_RECHAZADA
from enums import EstadoPago, MetodoPago
from excepciones import DatosDePagoInvalidosError


def procesador_efectivo(pago, datos):
    """Efectivo: queda pendiente hasta que se confirme en la app."""
    return EstadoPago.PENDIENTE


def procesador_transferencia(pago, datos):
    """Transferencia: queda pendiente hasta que se confirme en la app."""
    return EstadoPago.PENDIENTE


def procesador_tarjeta(pago, datos):
    """Valida el numero de tarjeta de prueba. El numero NO se guarda"""
    numero = (datos or {}).get('numero_tarjeta')
    if numero == NUMERO_TARJETA_APROBADA:
        return EstadoPago.APROBADO
    if numero == NUMERO_TARJETA_RECHAZADA:
        return EstadoPago.RECHAZADO
    raise DatosDePagoInvalidosError('Numero de tarjeta de prueba invalido')


PROCESADORES = {
    MetodoPago.EFECTIVO: procesador_efectivo,
    MetodoPago.TRANSFERENCIA: procesador_transferencia,
    MetodoPago.TARJETA: procesador_tarjeta,
}


def procesar(pago, datos=None) -> EstadoPago:
    """
    Busca el procesador del método de pago y devuelve el estado.

    Quien lo llame (el servicio) asigna: pago.estado = procesar(pago, datos)
    """
    return PROCESADORES[pago.metodo](pago, datos)
