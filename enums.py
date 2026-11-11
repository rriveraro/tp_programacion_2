# enums.py
from enum import Enum


class EstadoReserva(Enum):
    PENDIENTE = "PENDIENTE"
    ACEPTADA = "ACEPTADA"
    CANCELADA = "CANCELADA"
    EXPIRADA = "EXPIRADA"
    FINALIZADA = "FINALIZADA"


class MetodoPago(Enum):
    EFECTIVO = 'EFECTIVO'
    TRANSFERENCIA = 'TRANSFERENCIA'
    TARJETA = 'TARJETA'


class EstadoPago(Enum):
    PENDIENTE = 'PENDIENTE'
    APROBADO = 'APROBADO'
    RECHAZADO = 'RECHAZADO'
