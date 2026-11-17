from datetime import datetime
from decimal import Decimal

from sqlalchemy import ForeignKey, Numeric
from sqlalchemy.orm import Mapped, mapped_column

from paseos.core.database import Base
from paseos.reservas.enums import MotivoPenalidad


class Penalidad(Base):
    """Registro de penalidad aplicada a un usuario por infringir reglas de cancelación.
    En el MVP solo se registra (no se cobra).
    """

    __tablename__ = 'penalidades'

    id: Mapped[int] = mapped_column(primary_key=True)
    reserva_id: Mapped[int] = mapped_column(
        ForeignKey('reserva.id'), nullable=False
    )
    usuario_id: Mapped[int] = mapped_column(
        ForeignKey('usuarios.id'), nullable=False
    )
    motivo: Mapped[MotivoPenalidad]
    monto: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    creada_en: Mapped[datetime]

    def __init__(
        self,
        reserva_id: int,
        usuario_id: int,
        motivo: MotivoPenalidad,
        monto: Decimal,
        creada_en: datetime | None = None,
    ):
        self.reserva_id = reserva_id
        self.usuario_id = usuario_id
        self.motivo = motivo
        self.monto = monto
        self.creada_en = creada_en or datetime.now()
