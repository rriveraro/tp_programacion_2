"""Errores pertenecientes al módulo auth."""

from paseos.core.exceptions import NoAutenticado, SolicitudInvalida


class CredencialesInvalidas(NoAutenticado):
    mensaje = 'Email o contraseña incorrectos'


class TokenInvalido(NoAutenticado):
    mensaje = 'No se pudo validar el token'


class PasswordActualIncorrecta(SolicitudInvalida):
    mensaje = 'La contraseña actual es incorrecta'
