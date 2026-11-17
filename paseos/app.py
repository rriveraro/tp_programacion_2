from contextlib import asynccontextmanager
from fastapi import FastAPI

from paseos.auth.router import router as auth_router
from paseos.core.database import Base, engine
from paseos.core.exceptions import registrar_manejadores
from paseos.mascotas.router import router as mascotas_router
from paseos.pagos.router import router as pagos_router
from paseos.reservas.router import router as reservas_router
from paseos.usuarios.router import router as usuarios_router
from paseos.usuarios.repository import UsuarioRepository
from paseos.usuarios.router import get_usuario_service
from sqlalchemy.orm import Session
from paseos.reservas.repository import ReservaRepository
from fastapi import Depends
from paseos.core.database import Base, engine, get_db

# Importar todos los modelos antes de create_all para registrarlos en Base.metadata
from paseos.usuarios.models import Usuario  # noqa: F401
from paseos.mascotas.models import Mascota  # noqa: F401
from paseos.reservas.reservas import Reserva  # noqa: F401
from paseos.reservas.evento import EventoReserva  # noqa: F401
from paseos.reservas.penalidad import Penalidad  # noqa: F401
from paseos.pagos.pago import Pago
from paseos.usuarios.service import UsuarioService  # noqa: F401


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(title="API Gestión de Paseos Caninos", lifespan=lifespan)
registrar_manejadores(app)

app.include_router(auth_router)
app.include_router(usuarios_router)
app.include_router(mascotas_router)
app.include_router(reservas_router)
app.include_router(pagos_router)

# Composition Root: inyecta la verificación de reservas activas en usuarios sin import circular
def _get_usuario_service_con_reservas(db: Session = Depends(get_db)) -> UsuarioService:
    reserva_repo = ReservaRepository(db)
    return UsuarioService(
        repo=UsuarioRepository(db),
        tiene_reservas_activas=lambda usuario: reserva_repo.tiene_reservas_activas_usuario(usuario.id),
    )


app.dependency_overrides[get_usuario_service] = _get_usuario_service_con_reservas

@app.get("/")
def read_root():
    return {"message": "Hola Mundo!"}
