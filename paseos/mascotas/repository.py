"""acceso a datos de mascotas."""

from sqlalchemy.orm import Session

from paseos.mascotas.models import Mascota


class MascotaRepository:
    def __init__(self, db: Session):
        self.db = db

    def obtener_por_id(self, mascota_id: int) -> Mascota | None:
        return self.db.get(Mascota, mascota_id)