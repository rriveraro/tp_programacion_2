"""Excepciones de negocio del módulo de reservas."""

from paseos.core.exceptions import Conflicto, SolicitudInvalida


class ReservaError(SolicitudInvalida):
    mensaje = "Error de validación en la reserva"


class TurnoInvalidoError(ReservaError):
    mensaje = "El turno seleccionado no es válido"


class VacunaAntirrabicaNoVigenteError(ReservaError):
    mensaje = "La mascota no tiene la vacuna antirrábica vigente para la fecha del turno"


class TransicionInvalidaError(Conflicto):
    mensaje = "La operación no está permitida en el estado actual de la reserva"
