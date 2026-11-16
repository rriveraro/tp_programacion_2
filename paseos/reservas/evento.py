"""Modelo de auditoria de eventos de cambio de estado de una reserva. Ayuda a bloquear
que los paseadores vuelvan a aceptar cuadno ya cancelaron una misma reserva."""

from datetime import datetime

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from paseos.core.database import Base
from paseos.reservas.enums import AccionEvento
from paseos.reservas.reservas import Reserva


class EventoReserva(Base):
    """Registra cada transición de estado de una reserva y quién la ejecutó."""

    __tablename__ = "eventos_reserva"

    id: Mapped[int] = mapped_column(primary_key=True)
    reserva_id: Mapped[int] = mapped_column(ForeignKey("reserva.id"), nullable=False)
    usuario_id: Mapped[int | None] = mapped_column(ForeignKey("usuarios.id"), nullable=True)
    accion: Mapped[AccionEvento]
    creado_en: Mapped[datetime]
    

    def __init__(
        self,
        reserva_id: int,
        accion: AccionEvento,
        creado_en: datetime,
        usuario_id: int | None = None,
    ):
        self.reserva_id = reserva_id
        self.usuario_id = usuario_id
        self.accion = accion
        self.creado_en = creado_en