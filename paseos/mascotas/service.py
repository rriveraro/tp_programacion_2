from paseos.core.exceptions import Conflicto, NoAutorizado, NoEncontrado
from paseos.mascotas.models import Mascota
from paseos.mascotas.repository import MascotaRepository
from paseos.mascotas.schemas import MascotaActualizar, MascotaCrear
from paseos.reservas.repository import ReservaRepository
from paseos.usuarios.enums import Rol
from paseos.usuarios.models import Usuario


class MascotaService:
    def __init__(
        self,
        repo: MascotaRepository,
        reserva_repo: ReservaRepository | None = None,
    ):
        self.repo = repo
        self.reserva_repo = reserva_repo

    def _obtener_mascota_de_dueno(self, mascota_id: int, dueno: Usuario) -> Mascota:
        if dueno.rol != Rol.DUENO:
            raise NoAutorizado("Solo un usuario con rol DUENO puede gestionar mascotas")

        mascota = self.repo.obtener_por_id(mascota_id)
        if mascota is None:
            raise NoEncontrado(f"No existe la mascota con id {mascota_id}")
        if mascota.dueno_id != dueno.id:
            raise NoAutorizado("La mascota no pertenece al dueño autenticado")
        return mascota

    def registrar_mascota(self, dueno: Usuario, datos: MascotaCrear) -> Mascota:
        if dueno.rol != Rol.DUENO:
            raise NoAutorizado("Solo un usuario con rol DUENO puede registrar mascotas")

        mascota = Mascota(
            dueno_id=dueno.id,
            nombre=datos.nombre,
            fecha_nacimiento=datos.fecha_nacimiento,
            tamaño=datos.tamaño,
            raza=datos.raza,
            fecha_antirrabica=datos.fecha_antirrabica,
        )
        return self.repo.guardar(mascota)

    def listar_mis_mascotas(self, dueno: Usuario) -> list[Mascota]:
        if dueno.rol != Rol.DUENO:
            raise NoAutorizado("Solo un usuario con rol DUENO puede consultar sus mascotas")
        return self.repo.listar_por_dueno(dueno.id)

    def obtener_mascota(self, mascota_id: int, dueno: Usuario) -> Mascota:
        return self._obtener_mascota_de_dueno(mascota_id, dueno)

    def actualizar_mascota(
        self, mascota_id: int, dueno: Usuario, datos: MascotaActualizar
    ) -> Mascota:
        mascota = self._obtener_mascota_de_dueno(mascota_id, dueno)

        cambios = datos.model_dump(exclude_unset=True)
        for campo, valor in cambios.items():
            setattr(mascota, campo, valor)

        return self.repo.guardar(mascota)

    def eliminar_mascota(self, mascota_id: int, dueno: Usuario) -> None:
        mascota = self._obtener_mascota_de_dueno(mascota_id, dueno)

        if self.reserva_repo and self.reserva_repo.tiene_reservas_activas_mascota(
            mascota.id
        ):
            raise Conflicto(
                "No se puede eliminar una mascota que tiene reservas pendientes o aceptadas"
            )

        self.repo.eliminar(mascota)
