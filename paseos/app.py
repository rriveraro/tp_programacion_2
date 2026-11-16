from fastapi import FastAPI

from paseos.auth.router import router as auth_router
from paseos.core.exceptions import registrar_manejadores
from paseos.usuarios.router import router as usuarios_router
from paseos.reservas.router import router as reservas_router

app = FastAPI(title='API Gestión de Paseos Caninos')
registrar_manejadores(app)

# Cada módulo agrega acá su router.
app.include_router(auth_router)
app.include_router(usuarios_router)
app.include_router(reservas_router)

@app.get('/')
def read_root():
    return {'message': 'Hola Mundo!'}
