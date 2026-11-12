"""Excepciones base que se traducen a respuestas HTTP.

Idea: los servicios NO conocen HTTP. Lanzan excepciones de negocio que
heredan de estas clases, y un único manejador (registrado en app.py) las
convierte en la respuesta con el código que corresponde.

Ejemplo para otro módulo:
    class ReservaYaTomada(Conflicto):
        mensaje = 'La reserva ya fue aceptada por otro paseador'
"""

from http import HTTPStatus

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse


class AppError(Exception):
    """Base de todos los errores de negocio de la aplicación."""

    status_code: int = HTTPStatus.BAD_REQUEST
    mensaje: str = 'Error en la solicitud'

    def __init__(self, mensaje: str | None = None):
        super().__init__(mensaje or self.mensaje)
        self.mensaje = mensaje or self.mensaje


class SolicitudInvalida(AppError):
    status_code = HTTPStatus.BAD_REQUEST
    mensaje = 'Solicitud inválida'


class NoAutenticado(AppError):
    status_code = HTTPStatus.UNAUTHORIZED
    mensaje = 'No autenticado'


class NoAutorizado(AppError):
    status_code = HTTPStatus.FORBIDDEN
    mensaje = 'No tiene permiso para realizar esta acción'


class NoEncontrado(AppError):
    status_code = HTTPStatus.NOT_FOUND
    mensaje = 'Recurso no encontrado'


class Conflicto(AppError):
    status_code = HTTPStatus.CONFLICT
    mensaje = 'La operación entra en conflicto con el estado actual'


def registrar_manejadores(app: FastAPI) -> None:
    """Convierte cualquier AppError en una respuesta JSON con su código."""

    @app.exception_handler(AppError)
    async def manejar_app_error(_: Request, exc: AppError):
        headers = (
            {'WWW-Authenticate': 'Bearer'}
            if exc.status_code == HTTPStatus.UNAUTHORIZED
            else None
        )
        return JSONResponse(
            status_code=exc.status_code,
            content={'detail': exc.mensaje},
            headers=headers,
        )
