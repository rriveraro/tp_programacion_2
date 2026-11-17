"""Lógica de negocio del módulo reservas
Orquesta las validaciones de dominio, los cambios de estado sobre el modelo
Reserva, el registro de auditoría en EventoReserva y la persistencia mediante
ReservaRepository y MascotaRepository.
"""

from datetime import datetime, timedelta

from config import (
    HORA_MAXIMA_PASEO,
    HORA_MINIMA_PASEO,
    HORAS_ANTICIPACION_MINIMA,
    MAX_PERROS_SIMULTANEOS,
    MINUTOS_EXPIRAR_ANTES,
)
from paseos.core.exceptions import NoAutorizado, NoEncontrado
from paseos.mascotas.repository import MascotaRepository
from paseos.pagos.tarifa import calcular_comision, calcular_tarifa
from paseos.reservas.enums import AccionEvento, EstadoReserva, MotivoPenalidad
from paseos.reservas.evento import EventoReserva
from paseos.reservas.exceptions import (
    TransicionInvalidaError,
    TurnoInvalidoError,
    VacunaAntirrabicaNoVigenteError,
)
from paseos.reservas.penalidad import Penalidad
from paseos.reservas.repository import ReservaRepository
from paseos.reservas.reservas import Reserva
from paseos.reservas.schemas import ReservaCrear
from paseos.reservas.turno import Turno
from paseos.usuarios.enums import Barrio, Rol
from paseos.usuarios.models import Usuario


class ReservaService:
    def __init__(self, repo: ReservaRepository, mascota_repo: MascotaRepository):
        self.repo = repo
        self.mascota_repo = mascota_repo

    def _ahora(self, ahora: datetime | None) -> datetime:
        return ahora or datetime.now()

    def _obtener_reserva_o_fallar(self, reserva_id: int) -> Reserva:
        reserva = self.repo.obtener_por_id(reserva_id)
        if reserva is None:
            raise NoEncontrado(f"No existe la reserva con id {reserva_id}")
        return reserva

    def _validar_turno_creacion(self, turno: Turno, ahora: datetime) -> None:
        """Valida las reglas de negocio del turno al momento de crear la reserva."""
        if (turno.fecha.year, turno.fecha.month) != (ahora.year, ahora.month):
            raise TurnoInvalidoError(
                "Solo se pueden crear reservas dentro del mes actual"
            )
        if turno.hora_inicio < HORA_MINIMA_PASEO or turno.hora_fin > HORA_MAXIMA_PASEO:
            raise TurnoInvalidoError(
                "El horario del paseo debe estar entre las 08:00 y las 20:00"
            )
        if turno.inicio < ahora + timedelta(hours=HORAS_ANTICIPACION_MINIMA):
            raise TurnoInvalidoError(
                f"La reserva debe crearse con al menos {HORAS_ANTICIPACION_MINIMA} horas de anticipación"
            )

    def _expirar_vencidas(self, ahora: datetime) -> None:
        """Marca como EXPIRADA toda reserva PENDIENTE cuyo límite de aceptación ya pasó."""
        pendientes = self.repo.listar_pendientes()
        limite_para_expirar = timedelta(minutes=MINUTOS_EXPIRAR_ANTES)

        vencidas: list[Reserva] = []
        eventos: list[EventoReserva] = []

        for reserva in pendientes:
            if ahora >= reserva.turno.inicio - limite_para_expirar:
                reserva.expirar(ahora)
                vencidas.append(reserva)
                eventos.append(
                    EventoReserva(
                        reserva_id=reserva.id,
                        accion=AccionEvento.EXPIRADA,
                        creado_en=ahora,
                        usuario_id=None,
                    )
                )

        if vencidas:
            self.repo.guardar_varias(vencidas, eventos)

    def crear_reserva(
        self,
        dueno: Usuario,
        datos: ReservaCrear,
        ahora: datetime | None = None,
    ) -> Reserva:
        """Crea una reserva en estado PENDIENTE."""
        instante = self._ahora(ahora)

        if not dueno.activo:
            raise NoAutorizado("El usuario está dado de baja")
        if dueno.rol != Rol.DUENO:
            raise NoAutorizado("Solo un usuario con rol DUENO puede crear reservas")

        mascota = self.mascota_repo.obtener_por_id(datos.mascota_id)
        if mascota is None:
            raise NoEncontrado(f"No existe la mascota con id {datos.mascota_id}")
        if mascota.dueno_id != dueno.id:
            raise NoAutorizado("La mascota no pertenece al dueño autenticado")

        turno = Turno(
            fecha=datos.fecha,
            hora_inicio=datos.hora_inicio,
            hora_fin=datos.hora_fin,
        )
        self._validar_turno_creacion(turno, instante)

        if not mascota.tiene_antirrabica_vigente(turno.fecha):
            raise VacunaAntirrabicaNoVigenteError(
                "La mascota no tiene la vacuna antirrábica vigente para la fecha del turno"
            )

        tarifa = calcular_tarifa(mascota.tamaño)
        comision = calcular_comision(tarifa)

        reserva = Reserva(
            mascota_id=mascota.id,
            turno=turno,
            tarifa=tarifa,
            comision=comision,
            calle=dueno.calle,
            numero=dueno.numero,
            barrio=dueno.barrio,
            creada_en=instante,
        )

        evento = EventoReserva(
            reserva_id=None,  # Se asigna después de guardar la reserva
            accion=AccionEvento.CREADA,
            creado_en=instante,
            usuario_id=dueno.id,
        )
        return self.repo.guardar(reserva, evento)

    def listar_pendientes(
        self,
        paseador: Usuario,
        barrio: Barrio | None = None,
        ahora: datetime | None = None,
    ) -> list[Reserva]:
        instante = self._ahora(ahora)
        if paseador.rol != Rol.PASEADOR:
            raise NoAutorizado(
                "Solo un usuario con rol PASEADOR puede consultar reservas pendientes"
            )

        self._expirar_vencidas(instante)
        return self.repo.listar_pendientes(barrio=barrio)

    def listar_mis_reservas(
        self,
        usuario: Usuario,
        solo_activas: bool = False,
        ahora: datetime | None = None,
    ) -> list[Reserva]:
        """Lista las reservas propias según el rol del usuario"""
        instante = self._ahora(ahora)
        self._expirar_vencidas(instante)

        if usuario.rol == Rol.DUENO:
            return self.repo.listar_por_dueno(usuario.id, solo_activas=solo_activas)
        return self.repo.listar_por_paseador(usuario.id, solo_activas=solo_activas)

    def obtener_domicilio(
        self,
        reserva_id: int,
        paseador: Usuario,
        ahora: datetime | None = None,
    ) -> Reserva:
        """Devuelve la reserva con domicilio completo al paseador asignado """
        instante = self._ahora(ahora)
        self._expirar_vencidas(instante)

        reserva = self._obtener_reserva_o_fallar(reserva_id)
        if paseador.rol != Rol.PASEADOR or reserva.paseador_id != paseador.id:
            raise NoAutorizado(
                "Solo el paseador asignado puede consultar el domicilio de esta reserva"
            )
        if reserva.estado != EstadoReserva.ACEPTADA:
            raise TransicionInvalidaError(
                "El domicilio solo está disponible mientras la reserva está ACEPTADA"
            )
        return reserva

    def aceptar_reserva(
        self,
        reserva_id: int,
        paseador: Usuario,
        ahora: datetime | None = None,
    ) -> Reserva:
        """Asigna al paseador una reserva pendiente."""
        instante = self._ahora(ahora)
        if paseador.rol != Rol.PASEADOR:
            raise NoAutorizado(
                "Solo un usuario con rol PASEADOR puede aceptar reservas"
            )

        self._expirar_vencidas(instante)
        reserva = self._obtener_reserva_o_fallar(reserva_id)

        # 1. Validar estado primero (antes de ir a contar turnos o historial)
        if reserva.estado != EstadoReserva.PENDIENTE:
            raise TransicionInvalidaError(
                f"No se puede aceptar una reserva en estado {reserva.estado.value}"
            )

        # 2. Regla: no volver a aceptar si ya retiró su aceptación antes
        if self.repo.paseador_cancelo_antes(reserva.id, paseador.id):
            raise TransicionInvalidaError(
                "No podés volver a aceptar una reserva cuya aceptación ya cancelaste"
            )

        # 3. Regla: tope de perros simultáneos
        aceptadas_en_turno = self.repo.contar_aceptadas_en_turno(
            paseador_id=paseador.id,
            fecha=reserva.turno.fecha,
            hora_inicio=reserva.turno.hora_inicio,
            hora_fin=reserva.turno.hora_fin,
        )
        if aceptadas_en_turno >= MAX_PERROS_SIMULTANEOS:
            raise TransicionInvalidaError(
                f"Ya alcanzaste el máximo de {MAX_PERROS_SIMULTANEOS} mascotas simultáneas en ese turno"
            )

        reserva.aceptar(paseador.id, instante)
        evento = EventoReserva(
            reserva_id=reserva.id,
            accion=AccionEvento.ACEPTADA,
            creado_en=instante,
            usuario_id=paseador.id,
        )
        return self.repo.guardar(reserva, evento)

    def cancelar_por_dueno(
        self,
        reserva_id: int,
        dueno: Usuario,
        ahora: datetime | None = None,
    ) -> Reserva:
        """Cancela una reserva por decisión del dueño y registra penalidad si es tardía."""
        instante = self._ahora(ahora)
        self._expirar_vencidas(instante)
        reserva = self._obtener_reserva_o_fallar(reserva_id)

        if dueno.rol != Rol.DUENO or reserva.dueno_id != dueno.id:
            raise NoAutorizado(
                "Solo el dueño de la mascota puede cancelar esta reserva"
            )

        es_tardia = reserva.es_cancelacion_tardia(instante)
        reserva.cancelar_por_dueno(instante)

        evento = EventoReserva(
            reserva_id=reserva.id,
            accion=AccionEvento.CANCELADA_DUENO,
            creado_en=instante,
            usuario_id=dueno.id,
        )
        penalidad = (
            Penalidad(
                reserva_id=reserva.id,
                usuario_id=dueno.id,
                motivo=MotivoPenalidad.CANCELACION_DUENO,
                monto=reserva.calcular_penalidad(),
                creada_en=instante,
            )
            if es_tardia
            else None
        )
        return self.repo.guardar(reserva, evento, penalidad)

    def cancelar_aceptacion(
        self,
        reserva_id: int,
        paseador: Usuario,
        ahora: datetime | None = None,
    ) -> Reserva:
        """El paseador retira su aceptación; si es tardía, registra penalidad al paseador."""
        instante = self._ahora(ahora)
        self._expirar_vencidas(instante)
        reserva = self._obtener_reserva_o_fallar(reserva_id)

        if paseador.rol != Rol.PASEADOR or reserva.paseador_id != paseador.id:
            raise NoAutorizado(
                "Solo el paseador asignado puede cancelar la aceptación de esta reserva"
            )

        es_tardia = reserva.es_cancelacion_tardia(instante)
        paseador_penalizado_id = reserva.paseador_id  # Se guarda antes de limpiar paseador_id

        reserva.cancelar_aceptacion(instante)

        evento = EventoReserva(
            reserva_id=reserva.id,
            accion=AccionEvento.ACEPTACION_CANCELADA,
            creado_en=instante,
            usuario_id=paseador.id,
        )
        penalidad = (
            Penalidad(
                reserva_id=reserva.id,
                usuario_id=paseador_penalizado_id,
                motivo=MotivoPenalidad.CANCELACION_PASEADOR,
                monto=reserva.calcular_penalidad(),
                creada_en=instante,
            )
            if es_tardia
            else None
        )
        return self.repo.guardar(reserva, evento, penalidad)

    def listar_mis_penalidades(
        self, usuario: Usuario, ahora: datetime | None = None
    ) -> list[Penalidad]:
        """Devuelve las penalidades recibidas por el usuario autenticado."""
        return self.repo.listar_penalidades_por_usuario(usuario.id)

    def finalizar_reserva(
        self,
        reserva_id: int,
        paseador: Usuario,
        ahora: datetime | None = None,
    ) -> Reserva:
        """Marcar el paseo como finalizado al devolver la mascota"""
        instante = self._ahora(ahora)
        reserva = self._obtener_reserva_o_fallar(reserva_id)

        if paseador.rol != Rol.PASEADOR or reserva.paseador_id != paseador.id:
            raise NoAutorizado(
                "Solo el paseador asignado puede finalizar esta reserva"
            )

        reserva.finalizar(instante)
        evento = EventoReserva(
            reserva_id=reserva.id,
            accion=AccionEvento.FINALIZADA,
            creado_en=instante,
            usuario_id=paseador.id,
        )
        return self.repo.guardar(reserva, evento)
