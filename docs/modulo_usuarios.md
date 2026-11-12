# Módulo usuarios

## Archivos

| Archivo | Qué hace |
|---|---|
| `paseos/usuarios/enums.py` | `Rol` (DUENO, PASEADOR) y `Barrio` (los 48 de CABA) |
| `paseos/usuarios/models.py` | Modelo `Usuario` (tabla `usuarios`): `edad(hoy)`, `validar_edad(hoy)`, `dar_de_baja()`, `es_dueno()`, `es_paseador()` |
| `paseos/usuarios/schemas.py` | `UsuarioCrear` (registro), `UsuarioActualizar` (edición), `UsuarioPublico` (respuesta, sin contraseña) |
| `paseos/usuarios/repository.py` | Consultas a la base: por id, email y DNI, y guardar |
| `paseos/usuarios/service.py` | Reglas: email y DNI únicos, edad por rol, edición y baja lógica con 409 |
| `paseos/usuarios/exceptions.py` | Errores de negocio del módulo |
| `paseos/usuarios/router.py` | Endpoints `/usuarios/me` |
| `tests/test_usuarios_*.py` | 24 tests (modelo, servicio y API) |

## Endpoints

| Método | Ruta | Respuestas |
|---|---|---|
| GET | `/usuarios/me` | 200 · 401 |
| PATCH | `/usuarios/me` | 200 · 400 sin datos · 401 · 422 si intenta cambiar email, DNI, rol o fecha de nacimiento |
| DELETE | `/usuarios/me` | 204 · 401 · 409 con reservas pendientes o aceptadas |

Registro, login y cambio de contraseña están en el módulo **auth**.

## Lo que usuarios le ofrece al resto

- **auth (registro):** `UsuarioService.crear_usuario(datos, password_hash, hoy)`. Recibe la contraseña ya hasheada con `get_password_hash`. Valida email y DNI únicos (409) y la edad según el rol (400).
- **auth (login):** `UsuarioService.obtener_activo_por_email(email)`. Devuelve `None` si no existe o está dado de baja. El token se crea con `create_access_token({'sub': usuario.email})`.
- **Todos:** `from paseos.usuarios.models import Usuario` y `from paseos.usuarios.enums import Rol, Barrio`.
- **reservas:** la clave foránea es `usuarios.id`. Al crear una reserva, se copian `usuario.calle`, `usuario.numero` y `usuario.barrio`.

## Base compartida (propuesta en este PR)

| Archivo | Para qué |
|---|---|
| `paseos/core/database.py` | `Base` (de la que heredan todos los modelos) y `get_db()` |
| `paseos/core/exceptions.py` | Errores base con su código HTTP (`SolicitudInvalida` 400, `NoAutenticado` 401, `NoAutorizado` 403, `NoEncontrado` 404, `Conflicto` 409) y un manejador único |
| `paseos/core/dependencies.py` | `get_usuario_actual()`: devuelve el usuario del token. 401 si el token es inválido o el usuario está inactivo |
| `paseos/core/settings.py` | Se agregan `DATABASE_URL` y los límites de edad por rol |

Cómo lo usa cada módulo:

```python
from paseos.core.database import Base, get_db
from paseos.core.exceptions import Conflicto
from paseos.core.dependencies import get_usuario_actual


class ReservaYaTomada(Conflicto):
    mensaje = 'La reserva ya fue aceptada por otro paseador'
```

Para chequear el rol en un endpoint: `if not usuario.es_paseador(): raise NoAutorizado()`.

## Pendiente

- **reservas:** reemplazar `_sin_reservas` en `paseos/usuarios/service.py` por la consulta real de reservas PENDIENTE o ACEPTADA.
- **reservas:** `reserva.py` importa `from db import Base`. Tiene que ser `from paseos.core.database import Base`.

## Alembic

Para inicializarlo (una sola vez): `poetry run alembic init migrations`. Después, en `migrations/env.py`:

```python
from paseos.core.database import Base
from paseos.core.settings import settings
import paseos.usuarios.models  # noqa: F401  (cada módulo agrega su import)

config.set_main_option('sqlalchemy.url', settings.DATABASE_URL)
target_metadata = Base.metadata
```

Para crear y aplicar una migración (antes, siempre `git pull` de `main`):

```bash
poetry run alembic revision --autogenerate -m "crear tabla usuarios"
poetry run alembic upgrade head
```
