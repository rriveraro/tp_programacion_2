"""Errores de negocio del módulo usuarios."""

from paseos.core.exceptions import Conflicto, NoEncontrado, SolicitudInvalida


class UsuarioNoEncontrado(NoEncontrado):
    mensaje = 'Usuario no encontrado'


class EmailYaRegistrado(Conflicto):
    mensaje = 'El email ya está registrado'


class DniYaRegistrado(Conflicto):
    mensaje = 'El DNI ya está registrado'


class EdadFueraDeRango(SolicitudInvalida):
    mensaje = 'La edad no está dentro del rango permitido para el rol'


class SinCambios(SolicitudInvalida):
    mensaje = 'No se envió ningún dato para modificar'


class UsuarioConReservasActivas(Conflicto):
    mensaje = (
        'No se puede dar de baja: tiene reservas pendientes o aceptadas. '
        'Cancelalas primero.'
    )
