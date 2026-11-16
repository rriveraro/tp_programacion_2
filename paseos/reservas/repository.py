"""Acceso a datos de reservas y su historial de eventos.
"""

from datetime import date, time

from sqlalchemy import exists, func, or_, select
from sqlalchemy.orm import Session

from paseos.mascotas.models import Mascota
from paseos.reservas.enums import AccionEvento, EstadoReserva
from paseos.reservas.evento import EventoReserva
from paseos.reservas.reservas import Reserva
from paseos.usuarios.enums import Barrio


ACTIVOS = (EstadoReserva.PENDIENTE, EstadoReserva.ACEPTADA)


class ReservaRepository:
    def __init__(self, db: Session):
        self.db = db

    def obtener_por_id(self, reserva_id: int) -> Reserva | None:
        return self.db.get(Reserva, reserva_id)

    def guardar(self, reserva: Reserva, evento: EventoReserva | None = None) -> Reserva:
        """Persiste la reserva (y opcionalmente un evento) en la misma transacción."""
        self.db.add(reserva)
        if evento is not None:
            self.db.add(evento)
        self.db.commit()
        self.db.refresh(reserva)
        return reserva

    def guardar_varias(
        self, reservas: list[Reserva], eventos: list[EventoReserva]
    ) -> None:
        """Actualiza múltiples reservas y sus eventos en una única transacción."""
        self.db.add_all(reservas)
        self.db.add_all(eventos)
        self.db.commit() #No hay refresh, ya existian estas reservas

    def listar_pendientes(self, barrio: Barrio | None = None) -> list[Reserva]:
        """Lista las reservas pendientes, opcionalmente filtradas por barrio."""
        stmt = select(Reserva).where(Reserva.estado == EstadoReserva.PENDIENTE)
        if barrio is not None:
            stmt = stmt.where(Reserva.barrio == barrio)
        return list(self.db.scalars(stmt).all())

    def listar_por_dueno(
        self, dueno_id: int, solo_activas: bool = False
    ) -> list[Reserva]:
        """Lista las reservas de las mascotas de un dueño (todas o solo activas)."""
        stmt = (
            select(Reserva)
            .join(Mascota, Reserva.mascota_id == Mascota.id)
            .where(Mascota.dueno_id == dueno_id)
        )
        if solo_activas:
            stmt = stmt.where(Reserva.estado.in_(ACTIVOS))
        return list(self.db.scalars(stmt).all())

    def listar_por_paseador(
        self, paseador_id: int, solo_activas: bool = False
    ) -> list[Reserva]:
        """Lista las reservas asignadas a un paseador (todas o solo activas)."""
        stmt = select(Reserva).where(Reserva.paseador_id == paseador_id)
        if solo_activas:
            stmt = stmt.where(Reserva.estado.in_(ACTIVOS))
        return list(self.db.scalars(stmt).all())

    def contar_aceptadas_en_turno(
        self,
        paseador_id: int,
        fecha: date,
        hora_inicio: time,
        hora_fin: time,
    ) -> int:
        """Cuenta cuántas reservas ACEPTADAS tiene un paseador en un turno exacto."""
        stmt = select(func.count(Reserva.id)).where(
            Reserva.paseador_id == paseador_id,
            Reserva.estado == EstadoReserva.ACEPTADA,
            Reserva.fecha == fecha,
            Reserva.hora_inicio == hora_inicio,
            Reserva.hora_fin == hora_fin,
        )
        return self.db.scalar(stmt) or 0

    def paseador_cancelo_antes(self, reserva_id: int, paseador_id: int) -> bool:
        """Indica si el paseador ya retiró su aceptación en esta reserva."""
        stmt = select(
            exists().where(
                EventoReserva.reserva_id == reserva_id,
                EventoReserva.usuario_id == paseador_id,
                EventoReserva.accion == AccionEvento.ACEPTACION_CANCELADA,
            )
        )
        return bool(self.db.scalar(stmt))

    def tiene_reservas_activas_mascota(self, mascota_id: int) -> bool:
        """Verifica si una mascota tiene reservas PENDIENTE o ACEPTADA."""
        stmt = select(
            exists().where(
                Reserva.mascota_id == mascota_id,
                Reserva.estado.in_(ACTIVOS),
            )
        )
        return bool(self.db.scalar(stmt))

    def tiene_reservas_activas_usuario(self, usuario_id: int) -> bool:
        """Verifica si un usuario tiene reservas activas como dueño o como paseador."""
        stmt = select(
            exists().where(
                Reserva.estado.in_(ACTIVOS),
                or_(
                    Reserva.paseador_id == usuario_id,
                    Reserva.mascota.has(Mascota.dueno_id == usuario_id),
                ),
            )
        )
        return bool(self.db.scalar(stmt))