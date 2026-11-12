from http import HTTPStatus

import pytest

from paseos.core.exceptions import AppError
from paseos.pagos.excepciones import (
    ConfirmacionInvalidaError,
    DatosDePagoInvalidosError,
    PagoInvalidoError,
)


@pytest.mark.parametrize(
    ('error', 'codigo'),
    [
        (PagoInvalidoError, HTTPStatus.CONFLICT),
        (ConfirmacionInvalidaError, HTTPStatus.CONFLICT),
        (DatosDePagoInvalidosError, HTTPStatus.BAD_REQUEST),
    ],
)
def test_errores_de_pagos_tienen_su_codigo_http(error, codigo):
    assert issubclass(error, AppError)
    assert error.status_code == codigo


def test_el_mensaje_se_puede_personalizar():
    error = PagoInvalidoError('La reserva no está finalizada')
    assert error.mensaje == 'La reserva no está finalizada'