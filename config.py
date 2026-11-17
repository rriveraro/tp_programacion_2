from datetime import time
from decimal import Decimal

# config.py
MINUTOS_EXPIRAR_ANTES = 30
MINUTOS_CANCELACION_TARDIA = 30
MAX_PERROS_SIMULTANEOS = 4

# Reglas de reservas
HORA_MINIMA_PASEO = time(8, 0)
HORA_MAXIMA_PASEO = time(20, 0)
HORAS_ANTICIPACION_MINIMA = 2


# Numeros de tarjeta de prueba
NUMERO_TARJETA_APROBADA = '4111111111111111'
NUMERO_TARJETA_RECHAZADA = '4000000000000002'

# Reqs para calculo de tarifa
# DURACION_PASEO_MINUTOS = 60
PRECIO_BASE = Decimal('8000')
PORCENTAJE_COMISION = Decimal('0.15')
PORCENTAJE_PENALIDAD = Decimal('0.15')
FACTORES_TAMANO = {
    'PEQUEÑO': Decimal('1.10'),
    'MEDIANO': Decimal('1.20'),
    'GRANDE': Decimal('1.30'),
}
