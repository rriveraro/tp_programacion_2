# test_turno.py
from datetime import date, datetime, time

import pytest

from paseos.reservas.turno import Turno, TurnoInvalidoError

AHORA = datetime(2026, 11, 8, 12, 0)


def test_turno_valido_no_lanza_error():
    turno = Turno(date(2026, 11, 10), time(13, 15), time(14, 15))
    turno.validar_turno(AHORA)


def test_fin_anterior_o_igual_al_inicio_lanza_error():
    with pytest.raises(TurnoInvalidoError):
        Turno(date(2026, 11, 8), time(17, 0), time(13, 0))


def test_turno_en_el_pasado_lanza_error():
    turno = Turno(date(2026, 11, 7), time(13, 0), time(14, 0))
    with pytest.raises(TurnoInvalidoError):
        turno.validar_turno(AHORA)


def test_inicio_y_fin_combinan_fecha_y_hora():
    turno = Turno(date(2026, 11, 10), time(13, 15), time(14, 15))
    assert turno.inicio == datetime(2026, 11, 10, 13, 15)
    assert turno.fin == datetime(2026, 11, 10, 14, 15)