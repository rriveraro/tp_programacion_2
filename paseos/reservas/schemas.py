"""
Definen el contrato de entrada y salida de la API respetando la privacidad
del domicilio y la visibilidad de datos según el rol del usuario.

"""

from datetime import date, datetime, time
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from paseos.reservas.enums import EstadoReserva, MotivoPenalidad
from paseos.usuarios.enums import Barrio


class TurnoPublico(BaseModel):
    """Franja horaria de una reserva."""

    model_config = ConfigDict(from_attributes=True)

    fecha: date
    hora_inicio: time
    hora_fin: time


class ReservaCrear(BaseModel):
    """Datos que envía el dueño para crear una reserva.

    El dueño se toma del token JWT y el domicilio (calle, número, barrio)
    se copia automáticamente desde el perfil del dueño al momento de crearla.
    """

    model_config = ConfigDict(extra='forbid')

    mascota_id: int = Field(gt=0)
    fecha: date
    hora_inicio: time
    hora_fin: time


class ReservaDomicilio(BaseModel):
    """Domicilio completo de retiro/devolución.
    Solo accesible cuando la reserva está ACEPTADA y consulta el paseador asignado.
    """

    model_config = ConfigDict(from_attributes=True)

    calle: str
    numero: str
    barrio: Barrio


class ReservaBaseSalida(BaseModel):
    """Campos comunes visibles tanto para dueños como para paseadores."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    mascota_id: int
    dueno_id: int
    paseador_id: int | None
    turno: TurnoPublico
    estado: EstadoReserva
    barrio: Barrio
    tarifa: Decimal
    devuelta_en: datetime | None
    devolucion_tardia: bool


class ReservaPublica(ReservaBaseSalida):
    """Vista de la reserva para el paseador (incluye comisión, sin calle ni número)."""

    comision: Decimal


class ReservaDetalleDueno(ReservaBaseSalida):
    """Vista de la reserva para el dueño (incluye su domicilio, sin comisión)."""

    calle: str
    numero: str


class PenalidadSalida(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    reserva_id: int
    usuario_id: int
    motivo: MotivoPenalidad
    monto: Decimal
    creada_en: datetime
