from datetime import date, datetime, time, timedelta
from decimal import Decimal

from sqlalchemy import ForeignKey, Numeric
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.orm import Mapped, composite, mapped_column, relationship

from config import MINUTOS_CANCELACION_TARDIA
from paseos.core.database import Base
from paseos.mascotas.models import Mascota
from paseos.pagos.tarifa import calcular_penalidad
from paseos.reservas.enums import EstadoReserva
from paseos.reservas.estados import ESTADOS
from paseos.reservas.turno import Turno
from paseos.usuarios.enums import Barrio


class Reserva(Base):
    """Reserva de un paseo. El comportamiento depende del estado (patrón State)."""

    __tablename__ = "reserva"

    id: Mapped[int] = mapped_column(primary_key=True)
    mascota_id: Mapped[int] = mapped_column(ForeignKey("mascotas.id"), nullable=False)
    mascota: Mapped["Mascota"] = relationship()
    dueno_id = association_proxy("mascota", "dueno_id")

    fecha: Mapped[date]
    hora_inicio: Mapped[time]
    hora_fin: Mapped[time]
    turno: Mapped[Turno] = composite(Turno, "fecha", "hora_inicio", "hora_fin")

    estado: Mapped[EstadoReserva]
    paseador_id: Mapped[int | None] = mapped_column(
        ForeignKey("usuarios.id"), nullable=True
    )
    creada_en: Mapped[datetime]
    devuelta_en: Mapped[datetime | None]
    devolucion_tardia: Mapped[bool]
    tarifa: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    comision: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    calle: Mapped[str]
    numero: Mapped[str]
    barrio: Mapped[Barrio]

    def __init__(
        self,
        mascota_id: int,
        turno: Turno,
        tarifa: Decimal | None = None,
        comision: Decimal | None = None,
        calle: str | None = None,
        numero: str | None = None,
        barrio: Barrio | None = None,
        creada_en: datetime | None = None,
    ):
        self.mascota_id = mascota_id
        self.turno = turno
        self.estado = EstadoReserva.PENDIENTE
        self.paseador_id = None
        self.creada_en = creada_en or datetime.now()
        self.devolucion_tardia = False
        self.tarifa = tarifa
        self.comision = comision
        self.calle = calle
        self.numero = numero
        self.barrio = barrio

    @property
    def _state(self):
        return ESTADOS[self.estado]

    def aceptar(self, paseador_id: int, ahora: datetime) -> None:
        self._state.aceptar(self, paseador_id, ahora)

    def cancelar_por_dueno(self, ahora: datetime) -> None:
        self._state.cancelar_por_dueno(self, ahora)

    def cancelar_aceptacion(self, ahora: datetime) -> None:
        self._state.cancelar_aceptacion(self, ahora)

    def expirar(self, ahora: datetime) -> None:
        self._state.expirar(self, ahora)

    def finalizar(self, ahora: datetime) -> None:
        self._state.finalizar(self, ahora)

    def es_cancelacion_tardia(self, ahora: datetime) -> bool:
        limite = self.turno.inicio - timedelta(minutes=MINUTOS_CANCELACION_TARDIA)
        return ahora >= limite

    def ganancia_paseador(self) -> Decimal:
        return self.tarifa - self.comision

    def ganancia_paseador(self) -> Decimal:
        return self.tarifa - self.comision

    def calcular_penalidad(self) -> Decimal:
        """Delega el cálculo y redondeo de la penalidad al módulo de tarifas."""
        return calcular_penalidad(self.tarifa)
