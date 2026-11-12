# enums.py
from enum import Enum

class EstadoReserva(Enum):
    PENDIENTE = "PENDIENTE"
    ACEPTADA = "ACEPTADA"
    CANCELADA = "CANCELADA"
    EXPIRADA = "EXPIRADA"
    FINALIZADA = "FINALIZADA"
