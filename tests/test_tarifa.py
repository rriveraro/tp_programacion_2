from decimal import Decimal

import pytest

from paseos.mascotas.enums import Tamaño as Tamano
from paseos.pagos.tarifa import (
    calcular_comision,
    calcular_ganancia_neta,
    calcular_penalidad,
    calcular_tarifa,
)


@pytest.mark.parametrize(
    ('tamano', 'esperada'),
    [
        (Tamano.PEQUEÑO, Decimal('8800.00')),
        (Tamano.MEDIANO, Decimal('9600.00')),
        (Tamano.GRANDE, Decimal('10400.00')),
    ],
)
def test_tarifa_es_precio_base_por_factor_de_tamano(tamano, esperada):
    assert calcular_tarifa(tamano) == esperada


@pytest.mark.parametrize(
    ('tarifa', 'esperada'),
    [
        (Decimal('8800'), Decimal('1320.00')),
        (Decimal('9600'), Decimal('1440.00')),
        (Decimal('10400'), Decimal('1560.00')),
    ],
)
def test_comision_es_15_por_ciento_de_la_tarifa(tarifa, esperada):
    assert calcular_comision(tarifa) == esperada


@pytest.mark.parametrize(
    ('tarifa', 'esperada'),
    [
        (Decimal('8800'), Decimal('7480.00')),
        (Decimal('9600'), Decimal('8160.00')),
        (Decimal('10400'), Decimal('8840.00')),
    ],
)
def test_ganancia_neta_es_tarifa_menos_comision(tarifa, esperada):
    assert calcular_ganancia_neta(tarifa) == esperada


@pytest.mark.parametrize('tamano', list(Tamano))
def test_comision_mas_ganancia_es_la_tarifa(tamano):
    tarifa = calcular_tarifa(tamano)
    assert calcular_comision(tarifa) + calcular_ganancia_neta(tarifa) == tarifa


def test_redondea_a_centavos():
    # 1,01 x 15% = 0,1515 -> 0,15
    assert calcular_comision(Decimal('1.01')) == Decimal('0.15')


@pytest.mark.parametrize(
    ('tarifa', 'esperada'),
    [
        (Decimal('8800'), Decimal('1320.00')),
        (Decimal('9600'), Decimal('1440.00')),
        (Decimal('10400'), Decimal('1560.00')),
    ],
)
def test_penalidad_es_15_por_ciento_de_la_tarifa(tarifa, esperada):
    assert calcular_penalidad(tarifa) == esperada
