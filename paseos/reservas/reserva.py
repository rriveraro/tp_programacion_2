# reserva.py
from datetime import date, datetime, time, timedelta
from sqlalchemy import ForeignKey, Mapped, composite , relationship
from sqlalchemy import mapped_column, Numeric, Decimal, association_proxy
from config import MINUTOS_CANCELACION_TARDIA
from paseos.core.database import Base
from paseos.reservas.enums import EstadoReserva
from paseos.reservas.estados import ESTADOS
from paseos.reservas.turno import Turno, Barrio, Mascota
 
class Reserva(Base):
    """Reserva de un paseo. El comportamiento depende del estado (patrón State)."""

    __tablename__ = "reserva"

    id: Mapped[int] = mapped_column(primary_key=True)
    mascota_id: Mapped[int] = mapped_column(ForeignKey('mascotas.id'), nullable=False)
    mascota: Mapped['Mascota'] = relationship() #para que dueño tenga de donde sacarlo
    dueno_id = association_proxy('mascota', 'dueno_id') #para obtener el id del dueño de la mascota sin hacer join
    turno_id: Mapped[int] = composite(Turno, "fecha", "hora_inicio", "hora_fin")
    estado: Mapped[EstadoReserva]
    paseador_id: Mapped[int | None] = mapped_column(foreign_key="usuarios.id", nullable=True)
    devuelta_en: Mapped[datetime | None]
    devolucion_tardia: Mapped[bool]
    tarifa: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    comision: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    calle: Mapped[str]
    numero: Mapped[str]
    barrio: Mapped[Barrio]


    def __init__(self, mascota_id: int, turno: Turno): #no se si sirve pero el estado tiene que ser pendiente
        self.mascota_id = mascota_id
        self.turno = turno
        self.estado = EstadoReserva.PENDIENTE
        self.paseador_id= None
        self.devolucion_tardia = False

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