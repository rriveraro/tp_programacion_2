from enum import Enum

class MetodoPago(Enum):
    EFECTIVO = 'EFECTIVO'
    TRANSFERENCIA = 'TRANSFERENCIA'
    TARJETA = 'TARJETA'


class EstadoPago(Enum):
    PENDIENTE = 'PENDIENTE'
    APROBADO = 'APROBADO'
    RECHAZADO = 'RECHAZADO'