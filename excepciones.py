# excepciones.py
class ReservaError(Exception):
    """Base de las excepciones del módulo de reservas."""


class TurnoInvalidoError(ReservaError):
    """El turno rompe una regla de negocio."""


class TransicionInvalidaError(ReservaError):
    """La acción no está permitida en el estado actual de la reserva."""