from datetime import date
from typing_extensions import Annotated

from pydantic import BaseModel, ConfigDict, Field, field_validator

from paseos.core.validaciones import Nombre
from paseos.mascotas.enums import Tamaño


class _MascotaValidaciones(BaseModel):
    """Reglas de validación compartidas entre crear y modifcar de mascotas."""

    @field_validator('fecha_nacimiento', check_fields=False)
    @classmethod
    def validar_fecha_nacimiento(cls, valor: date | None) -> date | None:
        if valor is not None and valor > date.today():
            raise ValueError('La fecha de nacimiento no puede ser futura')
        return valor

    @field_validator('fecha_antirrabica', check_fields=False)
    @classmethod
    def validar_fecha_antirrabica(cls, valor: date | None) -> date | None:
        if valor is not None and valor > date.today():
            raise ValueError('La fecha de vacunación no puede ser futura')
        return valor


class MascotaCrear(_MascotaValidaciones):
    """Datos que envía el dueño para registrar una mascota."""

    model_config = ConfigDict(extra='forbid')

    nombre: str = Field(min_length=1, max_length=100)
    fecha_nacimiento: date
    tamaño: Tamaño
    raza: Annotated[Nombre, Field(min_length=2, max_length=100)]
    fecha_antirrabica: date | None = None


class MascotaActualizar(_MascotaValidaciones):
    """Datos opcionales para actualizar una mascota (incluye renovar antirrábica)."""

    model_config = ConfigDict(extra='forbid')

    nombre: str | None = Field(default=None, min_length=1, max_length=100)
    fecha_nacimiento: date | None = None
    tamaño: Tamaño | None = None
    raza: Annotated[Nombre, Field(default=None, min_length=2, max_length=100)]
    fecha_antirrabica: date | None = None


class MascotaPublica(BaseModel):
    """Representación de salida de una mascota."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    dueno_id: int
    nombre: str
    fecha_nacimiento: date
    tamaño: Tamaño
    raza: str
    fecha_antirrabica: date | None
