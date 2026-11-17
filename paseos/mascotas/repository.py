"""acceso a datos de mascotas."""

from sqlalchemy import select
from sqlalchemy.orm import Session

from paseos.mascotas.models import Mascota


class MascotaRepository:
    def __init__(self, db: Session):
        self.db = db

    def obtener_por_id(self, mascota_id: int) -> Mascota | None:
        return self.db.get(Mascota, mascota_id)

    def listar_por_dueno(self, dueno_id: int) -> list[Mascota]:
        stmt = select(Mascota).where(Mascota.dueno_id == dueno_id)
        return list(self.db.scalars(stmt).all())

    def guardar(self, mascota: Mascota) -> Mascota:
        self.db.add(mascota)
        self.db.commit()
        self.db.refresh(mascota)
        return mascota

    def eliminar(self, mascota: Mascota) -> None:
        self.db.delete(mascota)
        self.db.commit()
