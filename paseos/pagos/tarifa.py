"""Cálculos de tarifa: comisión de la app, precio base y ganancia del paseador.

Son funciones puras.
Los valores salen de config.py
"""

from decimal import ROUND_HALF_UP, Decimal

from config import (
    FACTORES_TAMANO,
    PORCENTAJE_COMISION,
    PORCENTAJE_PENALIDAD,
    PRECIO_BASE,
)
from paseos.mascotas.enums import Tamaño as Tamano

CENTAVOS = Decimal('0.01')


def _redondear(monto: Decimal) -> Decimal:
    return monto.quantize(CENTAVOS, rounding=ROUND_HALF_UP)


def calcular_tarifa(tamano: Tamano) -> Decimal:
    """Tarifa = precio base x factor de tamano."""
    return _redondear(PRECIO_BASE * FACTORES_TAMANO[tamano.value])


def calcular_comision(tarifa: Decimal) -> Decimal:
    """Comisión de la app = tarifa x porcentaje de comisión."""
    return _redondear(tarifa * PORCENTAJE_COMISION)


def calcular_ganancia_neta(tarifa: Decimal) -> Decimal:
    """Ganancia del paseador = tarifa - comisión."""
    return tarifa - calcular_comision(tarifa)


def calcular_penalidad(tarifa: Decimal) -> Decimal:
    """Penalidad = tarifa x porcentaje de penalidad."""
    return _redondear(tarifa * PORCENTAJE_PENALIDAD)
