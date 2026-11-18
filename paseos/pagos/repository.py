"""Acceso a datos de pagos.

capa que conecta con sqlalchemy. Le pide cosas como "busca por id" , "guarda", etc.
"""

from sqlalchemy import or_,select
from sqlalchemy.orm import Session

from paseos.pagos.enums import EstadoPago
from paseos.pagos.pago import Pago
from paseos.mascotas.models import Mascota
from paseos.reservas.reservas import Reserva


class RepositoryPago:
    def __init__(self, db: Session):
        self.db = db

    def get_pago_por_id(self, pago_id: int) -> Pago | None:
        return self.db.get(Pago, pago_id)

    def get_reserva_pagada(self, reserva_id: int) -> Pago | None:
        return self.db.scalar(
            select(Pago).where(
                Pago.reserva_id == reserva_id,
                Pago.estado != EstadoPago.RECHAZADO,
            )
        )

    def listar_de_usuario(self, usuario_id: int) -> list[Pago]:
        """Pagos donde el usuario es el paseador o el dueño de la mascota."""
        consulta = (
            select(Pago)
            .join(Reserva, Pago.reserva_id == Reserva.id)
            .join(Mascota, Reserva.mascota_id == Mascota.id)
            .where(
                or_(
                    Pago.paseador_id == usuario_id,
                    Mascota.dueno_id == usuario_id,
                )
            )
            .order_by(Pago.creado_en.desc())
        )
        return list(self.db.scalars(consulta))


    def guardar(self, pago: Pago) -> Pago:
        self.db.add(pago)
        self.db.commit()
        self.db.refresh(pago)
        return pago
