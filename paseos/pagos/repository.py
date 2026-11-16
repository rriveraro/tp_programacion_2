"""Acceso a datos de pagos.

capa que conecta con sqlalchemy. Le pide cosas como "busca por id" , "guarda", etc.
"""

from sqlalchemy import select
from sqlalchemy.orm import Session

from paseos.pagos.enums import EstadoPago
from paseos.pagos.pago import Pago


class RepositoryPago:
    def __init__(self, db: Session):
        self.db = db

    def get_pago_por_id(self, pago_id: int) -> Pago | None:
        return self.db.get(Pago, pago_id)

    def get_reserva_pagada(self, reserva_id: int) -> Pago | None:
        return self.db.scalar(
            select(Pago).where(
                Pago.reserva_id == reserva_id,
                Pago.estado != EstadoPago.RECHAZADO
            )
        )

    def guardar(self, pago: Pago) -> Pago:
        self.db.add(pago)
        self.db.commit()
        self.db.refresh(pago)
        return pago