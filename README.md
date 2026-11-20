# Yendog · API RESTful de Gestión de Paseos Caninos

[![Tests](https://github.com/rriveraro/tp_programacion_2/actions/workflows/tests.yml/badge.svg)](https://github.com/rriveraro/tp_programacion_2/actions/workflows/tests.yml)

Trabajo práctico final de **Programación 2** (Grupo 4). API para reservar paseos de perros en CABA: el dueño reserva un turno para su perro y cualquier paseador disponible lo acepta, con un tope de perros por turno. El domicilio del dueño se mantiene privado hasta que hay un paseador asignado.

| | |
|---|---|
| **API desplegada** | https://yendog.onrender.com |
| **Documentación interactiva (Swagger)** | https://yendog.onrender.com/docs |
| **Frontend** | https://yendog.onrender.com/app/ |
| **Documentación del proyecto** | [docs/documentacion.md](docs/documentacion.md): idea general, requerimientos funcionales y no funcionales, casos de uso, reglas de negocio |
| **Diagrama de clases** | [docs/Diagramas](docs/Diagramas/gesti%C3%B3n_paseos_MVP_actualizado.drawio.png) |

## Integrantes

| Integrante | Parte del proyecto |
|---|---|
| Florencia Montti | Usuarios, GitHub Action, Docker |
| Ludmila Cáceres | Autenticación y autorización |
| Agustina Sosa | Reservas, turnos, mascotas y patrón State |
| Rocío Rivera | Pagos y frontend |

## Qué hace

- Registro y login con **JWT**, con dos roles: **Dueño** y **Paseador**.
- El dueño registra sus perros y reserva paseos (dentro del mes actual, de 8 a 20 h, con al menos 2 horas de anticipación y la antirrábica vigente).
- El paseador ve las reservas pendientes (con filtro por barrio), las acepta hasta un tope de 4 perros por turno y, al terminar, registra la devolución.
- Cancelaciones con **penalidad** si faltan 30 minutos o menos, y **expiración** de las reservas que nadie aceptó.
- Cálculo de tarifa, comisión de la plataforma y ganancia del paseador.
- **Pagos simulados** con efectivo, transferencia o tarjeta de prueba.

## Librerías

**Producción** (definidas en `pyproject.toml`):

| Librería | Para qué se usa |
|---|---|
| `fastapi[standard]` | Framework de la API; incluye Uvicorn y la CLI `fastapi` |
| `sqlalchemy` | ORM y acceso a la base de datos |
| `pydantic-settings` | Configuración desde variables de entorno y `.env` |
| `pyjwt` | Creación y verificación de los tokens JWT |
| `pwdlib[argon2]` | Hash de contraseñas con Argon2 |
| `email-validator` | Validación de emails en los schemas de Pydantic |
| `alembic` | Migraciones de base de datos (instalada; hoy las tablas se crean al iniciar la app) |

**Desarrollo:** `pytest`, `pytest-cov`, `httpx` (cliente de pruebas), `ruff` (lint y formato) y `typos`.

## Correr la API localmente

Requisitos: **Python 3.14** y **[Poetry](https://python-poetry.org/docs/#installation) 2.x**.

```bash
git clone https://github.com/rriveraro/tp_programacion_2.git
cd tp_programacion_2
poetry env use python3.14
poetry install
cp .env.example .env              # en Windows: copy .env.example .env
```

En el `.env`, reemplazá `SECRET_KEY` por una clave larga y aleatoria. Se puede generar con:

```bash
python3 -c "import secrets; print(secrets.token_urlsafe(48))"
```

Levantar la API:

```bash
poetry run fastapi dev paseos/app.py
```

- Documentación interactiva: http://127.0.0.1:8000/docs
- Frontend: http://127.0.0.1:8000/app/

La base de datos es un archivo SQLite (`paseos.db`) que se crea solo la primera vez.

### Variables de entorno

| Variable | Obligatoria | Valor por defecto | Para qué sirve |
|---|---|---|---|
| `SECRET_KEY` | Sí, en producción | Una clave de desarrollo | Firma los tokens JWT |
| `DATABASE_URL` | No | `sqlite:///./paseos.db` | Conexión a la base de datos |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | No | `30` | Duración del token |
| `PORT` | No | `8000` | Puerto del contenedor Docker (lo define la plataforma de deploy) |

## Tests

```bash
poetry run pytest
```

Corre los **194 tests** (unitarios y de API) e informa la cobertura, que hoy es del 94 %. Cada test usa su propia base SQLite en memoria, así que no toca `paseos.db`.

Revisar el estilo del código:

```bash
poetry run ruff check
```

Una **GitHub Action** ([`.github/workflows/tests.yml`](.github/workflows/tests.yml)) instala el proyecto y corre ruff y los tests en cada push a `main` y en cada pull request.

## Correr la API con Docker

Requiere tener [Docker](https://www.docker.com/products/docker-desktop/) instalado y abierto.

```bash
docker build -t paseos-api .
docker run -p 8000:8000 -e SECRET_KEY=poner-una-clave-larga paseos-api
```

La documentación interactiva queda en http://localhost:8000/docs.

- `SECRET_KEY` es obligatoria en producción: es la clave con la que se firman los tokens JWT.
- La base de datos es SQLite dentro del contenedor: los datos se pierden al borrar el contenedor.
- Las plataformas de deploy indican el puerto con la variable `PORT`; el contenedor la usa automáticamente (si no existe, usa el 8000).

## Deploy en Render

La API está desplegada en **https://yendog.onrender.com** como un *Web Service* de Render construido con el `Dockerfile` del repositorio. Para desplegarla de nuevo:

1. En Render: **New → Web Service**, elegir este repositorio (o pegar su URL pública) y el runtime **Docker**.
2. En **Environment Variables**, agregar `SECRET_KEY` con una clave larga y aleatoria. Render define `PORT` solo.
3. **Create Web Service**. Para publicar cambios nuevos de `main`: **Manual Deploy → Deploy latest commit**.

Dos cosas a tener en cuenta del plan gratuito: el servicio se suspende si nadie lo usa (el primer pedido tarda un poco más), y como la base es SQLite, los datos se borran con cada deploy. Para que persistan, alcanza con apuntar `DATABASE_URL` a una base PostgreSQL, sin cambiar el código.

## Cómo probar la API

La forma más simple es desde **https://yendog.onrender.com/docs** (o `http://127.0.0.1:8000/docs` en local):

1. **Registrar un dueño** con `POST /auth/registro`:
   ```json
   {
     "email": "ana@ejemplo.com",
     "password": "clave-segura-123",
     "nombre": "Ana Pérez",
     "dni": "30111222",
     "fecha_nacimiento": "1990-05-20",
     "calle": "Gurruchaga",
     "numero": "1500",
     "barrio": "PALERMO",
     "rol": "DUENO"
   }
   ```
   Repetir con otro email y DNI y `"rol": "PASEADOR"` para tener un paseador.
2. **Iniciar sesión**: botón **Authorize** (arriba a la derecha), con el email en *username* y la contraseña. Swagger agrega el token a cada pedido.
3. **Como dueño**: crear un perro con `POST /mascotas` (con `fecha_antirrabica` de menos de un año) y una reserva con `POST /reservas`, para dentro de al menos 2 horas, entre las 8 y las 20, y dentro del mes actual.
4. **Como paseador** (cerrar sesión y entrar con la otra cuenta): ver `GET /reservas/pendientes`, aceptar con `POST /reservas/{id}/aceptar` y consultar el domicilio con `GET /reservas/{id}/domicilio`.
5. **Pagar**: una vez finalizada la reserva, `POST /pagos`. Con tarjeta, el número de prueba `4111111111111111` se aprueba y `4000000000000002` se rechaza. Efectivo y transferencia quedan pendientes hasta que el paseador los confirma con `POST /pagos/{id}/confirmar`.

También se puede recorrer el mismo flujo desde el frontend, en `/app/`.

Con `curl`, el login usa formulario (estándar OAuth2) y el token va en el header `Authorization`:

```bash
TOKEN=$(curl -s -X POST https://yendog.onrender.com/auth/login \
  -d "username=ana@ejemplo.com&password=clave-segura-123" | python3 -c "import sys, json; print(json.load(sys.stdin)['access_token'])")
curl https://yendog.onrender.com/usuarios/me -H "Authorization: Bearer $TOKEN"
```

## Endpoints

| Método | Endpoint | Quién | Qué hace |
|---|---|---|---|
| POST | `/auth/registro` | Público | Registra un usuario |
| POST | `/auth/login` | Público | Devuelve el token JWT |
| POST | `/auth/cambiar-password` | Usuario logueado | Cambia la contraseña |
| GET | `/usuarios/me` | Usuario logueado | Devuelve el perfil propio |
| PATCH | `/usuarios/me` | Usuario logueado | Edita nombre y domicilio |
| DELETE | `/usuarios/me` | Usuario logueado | Baja lógica (409 si tiene reservas activas) |
| POST | `/mascotas` | Dueño | Registra un perro |
| GET | `/mascotas` | Dueño | Lista sus perros |
| GET | `/mascotas/{id}` | Dueño | Consulta un perro |
| PATCH | `/mascotas/{id}` | Dueño | Edita un perro |
| DELETE | `/mascotas/{id}` | Dueño | Elimina un perro (409 si tiene reservas activas) |
| POST | `/reservas` | Dueño | Crea una reserva |
| GET | `/reservas/pendientes` | Paseador | Lista las reservas pendientes (admite `?barrio=`) |
| GET | `/reservas/mias` | Usuario logueado | Lista sus reservas |
| POST | `/reservas/{id}/aceptar` | Paseador | Acepta una reserva |
| POST | `/reservas/{id}/cancelar` | Dueño | Cancela una reserva |
| POST | `/reservas/{id}/retirar-aceptacion` | Paseador | Se retira de una reserva aceptada |
| POST | `/reservas/{id}/finalizar` | Paseador | Registra la devolución del perro |
| GET | `/reservas/{id}/domicilio` | Paseador asignado | Devuelve la dirección completa |
| GET | `/reservas/penalidades/mias` | Usuario logueado | Lista sus penalidades |
| POST | `/pagos` | Dueño | Paga una reserva finalizada |
| GET | `/pagos/mios` | Usuario logueado | Lista sus pagos |
| GET | `/pagos/{id}` | Dueño o paseador del pago | Consulta un pago |
| POST | `/pagos/{id}/confirmar` | Paseador | Aprueba o rechaza un pago pendiente |

Códigos de error: **400** regla de negocio · **401** sin token o token inválido · **403** sin permiso · **404** no existe · **409** conflicto con el estado actual · **422** datos inválidos.

## Estructura del proyecto

```
paseos/
├── app.py            # crea la app, registra los routers y sirve el frontend
├── core/             # lo compartido: settings, base de datos, seguridad, excepciones, dependencias
├── auth/             # registro, login y cambio de contraseña
├── usuarios/         # perfil y baja de usuarios
├── mascotas/         # perros de cada dueño
├── reservas/         # reservas, turnos, estados (patrón State), eventos y penalidades
└── pagos/            # pagos, procesadores por método (patrón Strategy) y tarifas
config.py             # parámetros de las reglas de negocio (horarios, topes, precios, porcentajes)
frontend/             # frontend en HTML, CSS y JavaScript
tests/                # tests con pytest
docs/                 # documentación del proyecto y diagrama de clases
```

Cada módulo está organizado **por capas**: `router.py` recibe el request y responde, `service.py` aplica las reglas de negocio, `repository.py` consulta la base con SQLAlchemy, los modelos definen las tablas y `schemas.py` (Pydantic) valida lo que entra y define lo que sale.

## Patrones de diseño

- **State** (`paseos/reservas/estados.py`): cada estado de la reserva (Pendiente, Aceptada, Cancelada, Expirada, Finalizada) es una clase que define qué acciones admite. Evita una cadena de `if` por estado y permite sumar estados sin tocar los existentes.
- **Strategy** (`paseos/pagos/procesadores.py`): cada método de pago tiene su propia función procesadora con la misma firma, y un diccionario elige la que corresponde. Sumar un método nuevo no obliga a modificar el servicio de pagos.

El detalle de las decisiones de diseño está en la [documentación del proyecto](docs/documentacion.md#9-decisiones-de-diseño-y-patrones).
