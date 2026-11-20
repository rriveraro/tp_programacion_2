# API RESTful: Gestión de Paseos Caninos (Yendog)

**Grupo 4:** Sosa Agustina, Rivera Rocío, Montti Florencia, Cáceres Ludmila

**Repositorio:** <https://github.com/rriveraro/tp_programacion_2>

**Stack:** Python, FastAPI, SQLAlchemy, JWT, Pydantic, Pytest, Docker, GitHub Actions, despliegue en Render.

# 1. Síntesis

- Aplicación para reservar paseos de perros entre dueños y paseadores.

- Zona de lanzamiento prevista: CABA (lista fija de 48 barrios).

- Servicio exclusivo de paseo de perros.

# 2. Introducción

En el contexto urbano actual, la demanda de servicios de cuidado y ejercitación de mascotas crece de forma constante. Sin embargo, la oferta suele coordinarse por canales informales (mensajes, redes sociales, recomendaciones), sin una plataforma centralizada que garantice la seguridad de las partes, el cumplimiento de requisitos sanitarios básicos ni el control de la capacidad real de cada paseador.

Este proyecto propone una API RESTful que digitaliza y ordena la interacción entre dueños de mascotas y paseadores. El dueño reserva un paseo para su mascota en un turno determinado y cualquier paseador disponible puede tomarlo, dentro de un tope de mascotas por turno. Dado el alcance de la materia, el desarrollo se planificó de forma incremental: primero un **Producto Mínimo Viable (MVP)** que resuelve el núcleo del problema, y una visión de producto más amplia como implementación futura.

# 3. Glosario

- **Dueño:** usuario con rol DUENO que reserva paseos para sus mascotas.

- **Paseador:** usuario con rol PASEADOR que acepta reservas y realiza los paseos. Cada cuenta tiene un solo rol.

- **Mascota:** perro del dueño, con nombre, fecha de nacimiento, tamaño (Pequeño, Mediano, Grande), raza y fecha de la última vacuna antirrábica.

- **Turno:** franja horaria de un día determinado, con hora de inicio y de fin, dentro del horario de 8:00 a 20:00. Se usa para controlar el tope de mascotas por paseador. No tiene estado propio.

- **Reserva:** pedido de un dueño para que una de sus mascotas sea paseada en un turno. Tiene un estado a lo largo de su ciclo de vida.

- **Paseo:** el servicio en sí, que se realiza durante el turno de una reserva aceptada.

- **Penalidad:** registro del monto que corresponde a quien cancela fuera de plazo. En el MVP solo se registra, no se cobra.

- **Pago:** registro del pago de una reserva finalizada, simulado (sin pasarela real).

# 4. Alcance del MVP

## 4.1 Objetivo

Permitir que un dueño reserve un paseo para su mascota en un turno determinado y que cualquier paseador pueda aceptar esa reserva respetando el tope de mascotas por turno. El sistema resguarda el domicilio del dueño hasta que el paseador es asignado y controla la cancelación, la expiración y la devolución de la mascota.

## 4.2 Qué se logró

- Registro, login con JWT y roles Dueño y Paseador, con cambio de contraseña.

- Gestión de perfil propio y baja lógica de usuarios (se conserva el historial).

- Gestión de mascotas por parte del dueño, con control de vacuna antirrábica vigente al crear la reserva.

- Creación de reservas con anticipación mínima de 2 horas y horario de 8:00 a 20:00.

- Listado de reservas pendientes para el paseador, con filtro opcional por barrio.

- Aceptación con control del tope de mascotas por turno y bloqueo de re-aceptación tras haber cancelado.

- Cancelación por el dueño y retiro de la aceptación por el paseador, con penalidad registrada si faltan 30 minutos o menos.

- Expiración automática de reservas sin aceptar, resuelta al momento de consultar (sin tareas programadas).

- Finalización del paseo con registro de devolución y marca de devolución tardía.

- Privacidad del domicilio, donde el paseador solo ve el barrio hasta ser asignado (la reserva es aceptada).

- Cálculo de tarifa, comisión de la plataforma y ganancia neta del paseador.

- Historial de eventos de cada reserva (EventoReserva), registrado en la misma transacción que el cambio de estado.

- Pagos simulados por efectivo, transferencia o tarjeta, con arquitectura preparada para incorporar una pasarela real.

- Pruebas automatizadas (194 tests, 94 % de cobertura), GitHub Action, contenedor Docker y despliegue en Render.

- Frontend básico en HTML/JS servido por la misma API en /app, para probar los endpoints.

# 5. Requerimientos funcionales

Cada requerimiento describe una única acción de un actor (o una única responsabilidad del sistema). Las reglas de detalle (plazos, topes, montos) están en la sección 8.3 y los parámetros en la 8.4. Los requerimientos se agrupan por sección y cada una incluye la tabla de endpoints que los implementan. El estado refleja lo que existe hoy en el repositorio.

## 5.1 Autenticación y usuarios

| **Código** | **Requerimiento**                                                            | **Actor**        | **Estado**   |
|------------|------------------------------------------------------------------------------|------------------|--------------|
| RF01       | Registrar usuario: Crea su cuenta eligiendo un rol.                          | Dueño / Paseador | Implementado |
| RF02       | Validar datos de registro: Valida email y DNI únicos y la edad según el rol. | Sistema          | Implementado |
| RF03       | Proteger la contraseña: Guarda la contraseña hasheada.                       | Sistema          | Implementado |
| RF04       | Iniciar sesión: Se autentica con email y contraseña y recibe un token JWT.   | Dueño / Paseador | Implementado |
| RF05       | Cambiar contraseña: Cambia su contraseña verificando la actual.              | Dueño / Paseador | Implementado |
| RF06       | Consultar perfil: Consulta sus propios datos.                                | Dueño / Paseador | Implementado |
| RF07       | Editar perfil: Edita sus datos permitidos.                                   | Dueño / Paseador | Implementado |
| RF08       | Darse de baja: Se da de baja de forma lógica.                                | Dueño / Paseador | Implementado |

### Endpoints

| **Método** | **Endpoint**           | **Actor**        | **Qué hace**               | **RF**  |
|------------|------------------------|------------------|----------------------------|---------|
| **POST**   | /auth/registro         | Público          | Registra un usuario nuevo. | RF01–03 |
| **POST**   | /auth/login            | Público          | Devuelve el token JWT.     | RF04    |
| **POST**   | /auth/cambiar-password | Dueño / Paseador | Cambia la contraseña.      | RF05    |
| **GET**    | /usuarios/me           | Dueño / Paseador | Devuelve el perfil propio. | RF06    |
| **PATCH**  | /usuarios/me           | Dueño / Paseador | Edita el perfil propio.    | RF07    |
| **DELETE** | /usuarios/me           | Dueño / Paseador | Baja lógica del usuario.   | RF08    |

## 5.2 Mascotas

| **Código** | **Requerimiento**                                           | **Actor** | **Estado**   |
|------------|-------------------------------------------------------------|-----------|--------------|
| RF09       | Registrar mascota: Da de alta una mascota propia.           | Dueño     | Implementado |
| RF10       | Listar mascotas: Lista sus mascotas.                        | Dueño     | Implementado |
| RF11       | Consultar mascota: Consulta una de sus mascotas.            | Dueño     | Implementado |
| RF12       | Editar mascota: Edita los datos de una mascota.             | Dueño     | Implementado |
| RF13       | Eliminar mascota: Elimina una mascota sin reservas activas. | Dueño     | Implementado |

### Endpoints

| **Método** | **Endpoint**   | **Actor** | **Qué hace**                | **RF** |
|------------|----------------|-----------|-----------------------------|--------|
| **POST**   | /mascotas      | Dueño     | Registra una mascota.       | RF09   |
| **GET**    | /mascotas      | Dueño     | Lista las mascotas propias. | RF10   |
| **GET**    | /mascotas/{id} | Dueño     | Consulta una mascota.       | RF11   |
| **PATCH**  | /mascotas/{id} | Dueño     | Edita una mascota.          | RF12   |
| **DELETE** | /mascotas/{id} | Dueño     | Elimina una mascota.        | RF13   |

## 5.3 Reservas

| **Código** | **Requerimiento**                                                                 | **Actor**        | **Estado**   |
|------------|-----------------------------------------------------------------------------------|------------------|--------------|
| RF15       | Crear reserva: Reserva un turno para una de sus mascotas.                         | Dueño            | Implementado |
| RF16       | Validar turno: Verifica horario de 8:00 a 20:00 y anticipación mínima.            | Sistema          | Implementado |
| RF17       | Validar antirrábica: Verifica que la vacuna esté vigente a la fecha del turno.    | Sistema          | Implementado |
| RF18       | Listar reservas pendientes: Ve las reservas disponibles para aceptar.             | Paseador         | Implementado |
| RF19       | Filtrar por barrio: Filtra las pendientes por barrio.                             | Paseador         | Implementado |
| RF20       | Aceptar reserva: Toma una reserva pendiente y queda asignado.                     | Paseador         | Implementado |
| RF21       | Controlar tope por turno: Rechaza la aceptación si se supera el tope de mascotas. | Sistema          | Implementado |
| RF22       | Consultar mis reservas: Consulta sus reservas y su estado.                        | Dueño / Paseador | Implementado |
| RF23       | Cancelar reserva: Cancela una reserva pendiente o aceptada.                       | Dueño            | Implementado |
| RF24       | Retirar aceptación: Se retira de una reserva aceptada, que vuelve a Pendiente.    | Paseador         | Implementado |
| RF25       | Expirar reservas: Marca como expiradas las pendientes vencidas, al consultar.     | Sistema          | Implementado |
| RF26       | Finalizar reserva: Registra la devolución de la mascota.                          | Paseador         | Implementado |
| RF27       | Marcar devolución tardía: Marca la devolución posterior al fin del turno.         | Sistema          | Implementado |
| RF28       | Registrar historial: Guarda un evento por cada cambio de estado.                  | Sistema          | Implementado |
| RF29       | Ver domicilio completo: Consulta la dirección solo si es el paseador asignado.    | Paseador         | Implementado |
| RF30       | Resguardar domicilio: Muestra solo el barrio mientras la reserva está pendiente.  | Sistema          | Implementado |

### Endpoints

| **Método** | **Endpoint**                      | **Actor**        | **Qué hace**                        | **RF**           |
|------------|-----------------------------------|------------------|-------------------------------------|------------------|
| **POST**   | /reservas                         | Dueño            | Crea una reserva.                   | RF15–17          |
| **GET**    | /reservas/pendientes              | Paseador         | Lista pendientes (admite ?barrio=). | RF18, 19, 25, 30 |
| **POST**   | /reservas/{id}/aceptar            | Paseador         | Acepta la reserva.                  | RF20, 21         |
| **GET**    | /reservas/mias                    | Dueño / Paseador | Lista las reservas propias.         | RF22             |
| **POST**   | /reservas/{id}/cancelar           | Dueño            | Cancela la reserva.                 | RF23             |
| **POST**   | /reservas/{id}/retirar-aceptacion | Paseador         | Retira la aceptación.               | RF24             |
| **POST**   | /reservas/{id}/finalizar          | Paseador         | Registra la devolución.             | RF26, 27         |
| **GET**    | /reservas/{id}/domicilio          | Paseador         | Devuelve la dirección completa.     | RF29             |

*RF25 se ejecuta al consultar o aceptar, y RF28 en cada cambio de estado; no tienen endpoint propio.*

## 5.4 Tarifas y penalidades

| **Código** | **Requerimiento**                                                                      | **Actor**        | **Estado**   |
|------------|----------------------------------------------------------------------------------------|------------------|--------------|
| RF31       | Calcular tarifa: Calcula la tarifa según el tamaño de la mascota.                      | Sistema          | Implementado |
| RF32       | Calcular comisión y ganancia: Calcula la comisión de la plataforma y la ganancia neta. | Sistema          | Implementado |
| RF33       | Penalizar cancelación tardía: Registra la penalidad a quien infringe el plazo.         | Sistema          | Implementado |
| RF34       | Consultar mis penalidades: Consulta las penalidades recibidas.                         | Dueño / Paseador | Implementado |

### Endpoints

| **Método** | **Endpoint**               | **Actor**        | **Qué hace**                     | **RF** |
|------------|----------------------------|------------------|----------------------------------|--------|
| **GET**    | /reservas/penalidades/mias | Dueño / Paseador | Lista las penalidades recibidas. | RF34   |

*RF31 a RF33 los ejecuta el sistema al crear, cancelar o retirar una reserva.*

## 5.5 Pagos

| **Código** | **Requerimiento**                                           | **Actor**        | **Estado**   |
|------------|-------------------------------------------------------------|------------------|--------------|
| RF35       | Registrar pago: Paga una reserva finalizada (una sola vez). | Dueño            | Implementado |
| RF36       | Confirmar pago: Aprueba o rechaza un pago en efectivo o por transferencia.      | Paseador         | Implementado |
| RF37       | Listar mis pagos: Lista sus pagos.                          | Dueño / Paseador | Implementado |
| RF38       | Consultar un pago: Consulta el detalle de un pago.          | Dueño / Paseador | Implementado |

### Endpoints

| **Método** | **Endpoint**          | **Actor**        | **Qué hace**                     | **RF** |
|------------|-----------------------|------------------|----------------------------------|--------|
| **POST**   | /pagos                | Dueño            | Registra el pago de una reserva. | RF35   |
| **POST**   | /pagos/{id}/confirmar | Paseador         | Aprueba o rechaza el pago.       | RF36   |
| **GET**    | /pagos/mios           | Dueño / Paseador | Lista los pagos propios.         | RF37   |
| **GET**    | /pagos/{id}           | Dueño / Paseador | Consulta un pago.                | RF38   |

**Notas:** los permisos se verifican con el rol que viaja en el token (401 si no está autenticado, 403 si no está autorizado). El identificador del dueño se toma siempre del token, nunca de lo que envía el cliente. La notificación ante cambios de estado quedó en la visión futura (sección 10).

# 6. Requerimientos no funcionales

Se listan los requerimientos principales, cada uno con la forma en que se cumple en el proyecto.

| **Código** | **Categoría**             | **Requerimiento**                                                                                                                      | **Cómo se cumple**                                                                                                                               | **Estado** |
|------------|---------------------------|----------------------------------------------------------------------------------------------------------------------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------|------------|
| RNF01      | Seguridad: autenticación  | Las contraseñas se almacenan hasheadas y el acceso se controla con tokens JWT con vencimiento. La clave de firma no está en el código. | Hash de contraseñas, JWT de 30 minutos, SECRET_KEY por variable de entorno.                                                                      | Cumplido   |
| RNF02      | Seguridad: autorización   | Cada usuario opera según su rol y solo accede a sus propios recursos. Los fallos de login no revelan si el email existe.               | Rol dentro del token, validaciones en los servicios, 401/403 diferenciados y mensaje de login genérico.                                          | Cumplido   |
| RNF03      | Privacidad                | El domicilio del dueño no se expone hasta que el paseador es asignado.                                                                 | Mientras la reserva está pendiente solo se muestra el barrio. La dirección se obtiene con un endpoint restringido.                               | Cumplido   |
| RNF04      | Integridad de datos       | Los cambios de estado y su evento de historial deben guardarse juntos o no guardarse. Los importes no deben tener errores de redondeo. | Reserva y evento en la misma transacción: montos con Decimal, baja lógica de usuarios, domicilio copiado a la reserva.                           | Cumplido   |
| RNF05      | Trazabilidad              | Debe poder reconstruirse quién hizo cada cambio sobre una reserva.                                                                     | Tabla EventoReserva con acción, usuario (vacío cuando actúa el sistema) y fecha.                                                                 | Cumplido   |
| RNF06      | Mantenibilidad            | El código se organiza por módulos de dominio y por capas con responsabilidades separadas.                                              | Módulos auth, usuarios, mascotas, reservas y pagos, cada uno con router, servicio y repositorio; configuración centralizada.                     | Cumplido   |
| RNF07      | Extensibilidad            | Agregar estados, métodos de pago o reglas no debe obligar a reescribir lo existente.                                                   | Patrón State para las reservas; procesadores de pago intercambiables seleccionados por método (Strategy y fábrica simple).                       | Cumplido   |
| RNF08      | Testabilidad              | Las reglas que dependen del tiempo deben poder probarse con fechas fijas, y las pruebas deben ejecutarse automáticamente.              | El parámetro ahora se recibe desde afuera; 194 tests con pytest (94 % de cobertura); GitHub Action en cada push y pull request.                                 | Cumplido   |
| RNF09      | Consistencia de la API    | La API sigue principios RESTful, usa códigos HTTP adecuados, valida las entradas y maneja los errores con excepciones.                 | Excepciones de negocio con su código HTTP y un manejador único; validación con Pydantic; documentación OpenAPI en /docs.                         | Cumplido   |
| RNF10      | Portabilidad y despliegue | La aplicación debe poder ejecutarse en cualquier entorno de forma reproducible.                                                        | Contenedor Docker, configuración por variables de entorno, despliegue en Render.                                                                 | Cumplido   |
| RNF11      | Persistencia              | Los datos deben persistir entre reinicios y despliegues del servicio.                                                                  | La base se configura con DATABASE_URL. Hoy se usa SQLite, que en el contenedor se pierde al recrearlo; para producción se recomienda PostgreSQL. | Parcial    |
| RNF12      | Rendimiento               | La expiración de reservas no debe requerir procesos en segundo plano.                                                                  | Se resuelve al consultar. No se hicieron pruebas de carga, por lo que el rendimiento bajo alta demanda no está medido.                           | Parcial    |

# 7. Casos de uso

Se detallan los 10 casos de uso principales. Las consultas de reservas propias, el cambio de contraseña y la gestión del perfil siguen el mismo patrón y se describen en las tablas de requerimientos de la sección 5.

### CU01 – Registrarse

- **Actor:** Dueño o Paseador
- **Requerimientos:** RF01, RF02, RF03
- **Precondiciones:** No tener una cuenta con el mismo email o DNI.
- **Flujo principal:**
    1. El usuario envía nombre, email, contraseña, DNI, fecha de nacimiento, domicilio (calle, número, barrio) y rol.
    2. El sistema valida los datos y la edad permitida para el rol.
    3. El sistema guarda la contraseña hasheada y crea la cuenta activa.
- **Flujos alternativos / errores:**
    - a) Email o DNI ya registrados: error 409.
    - b) Edad fuera del rango del rol (menor de 18, mayor de 99 para dueño o de 65 para paseador): error 400.
    - c) Datos inválidos (contraseña corta, barrio inexistente): error 422.
- **Postcondición:** Existe un usuario activo con el rol elegido.

### CU02 – Iniciar sesión

- **Actor:** Dueño o Paseador
- **Requerimientos:** RF04
- **Precondiciones:** Tener una cuenta activa.
- **Flujo principal:**
    1. El usuario envía email y contraseña.
    2. El sistema verifica las credenciales.
    3. El sistema devuelve un token JWT que el usuario usa en las siguientes solicitudes.
- **Flujos alternativos / errores:**
    - a) Credenciales incorrectas o usuario inactivo: error 401 con mensaje genérico.
- **Postcondición:** El usuario queda autenticado mientras el token sea válido.

### CU03 – Gestionar mascotas

- **Actor:** Dueño
- **Requerimientos:** RF09, RF10, RF11, RF12, RF13
- **Precondiciones:** Estar autenticado con rol Dueño.
- **Flujo principal:**
    1. El dueño registra una mascota con nombre, fecha de nacimiento, tamaño, raza y fecha de antirrábica.
    2. El dueño puede listar, consultar y editar sus mascotas.
    3. El dueño puede eliminar una mascota que no tenga reservas activas.
- **Flujos alternativos / errores:**
    - a) Mascota ajena o inexistente: error 403 o 404.
    - b) Eliminar una mascota con reservas pendientes o aceptadas: error 409; primero hay que cancelarlas.
- **Postcondición:** Los datos de las mascotas del dueño quedan actualizados.

### CU04 – Crear reserva

- **Actor:** Dueño
- **Requerimientos:** RF15, RF16, RF17, RF28, RF31, RF32
- **Precondiciones:** Estar autenticado como Dueño y tener una mascota registrada.
- **Flujo principal:**
    1. El dueño elige mascota, día y horario del turno.
    2. El sistema valida rol, propiedad de la mascota, horario permitido, anticipación mínima y vacuna antirrábica vigente a la fecha del turno.
    3. El sistema calcula tarifa y comisión, copia el domicilio del dueño y crea la reserva en estado Pendiente.
    4. El sistema registra el evento de creación.
- **Flujos alternativos / errores:**
    - a) Mascota ajena: error 403; mascota inexistente: error 404.
    - b) Turno fuera de 8:00–20:00 o con menos de 2 horas de anticipación: error de turno inválido.
    - c) Antirrábica vencida o sin registrar: error de vacuna no vigente.
- **Postcondición:** Existe una reserva Pendiente visible para los paseadores.

### CU05 – Listar reservas pendientes

- **Actor:** Paseador
- **Requerimientos:** RF18, RF19, RF25, RF30
- **Precondiciones:** Estar autenticado como Paseador.
- **Flujo principal:**
    1. El paseador solicita el listado, opcionalmente filtrando por barrio.
    2. El sistema marca como expiradas las pendientes vencidas.
    3. El sistema devuelve las reservas pendientes restantes, mostrando solo el barrio.
- **Flujos alternativos / errores:**
    - a) Usuario con rol Dueño: error 403.
    - b) Barrio inexistente en el filtro: error 422.
- **Postcondición:** El listado solo incluye reservas todavía disponibles.

### CU06 – Aceptar reserva

- **Actor:** Paseador
- **Requerimientos:** RF20, RF21, RF28
- **Precondiciones:** Existe una reserva Pendiente.
- **Flujo principal:**
    1. El paseador elige una reserva del listado.
    2. El sistema verifica que siga pendiente, que el paseador no la haya cancelado antes y que no supere el tope de mascotas del turno.
    3. El sistema asigna al paseador, pasa la reserva a Aceptada y registra el evento.
- **Flujos alternativos / errores:**
    - a) Reserva ya tomada, expirada o cancelada: error de transición inválida.
    - b) El paseador ya había retirado su aceptación: error de transición inválida.
    - c) Tope de mascotas por turno alcanzado: error de transición inválida.
- **Postcondición:** La reserva queda Aceptada y asignada al paseador.

### CU07 – Cancelar reserva o retirar aceptación

- **Actor:** Dueño (cancela la reserva) o Paseador (retira su aceptación)
- **Requerimientos:** RF23, RF24, RF28, RF33, RF34
- **Precondiciones:** La reserva está Pendiente o Aceptada y el turno no comenzó.
- **Flujo principal:**
    1. El dueño cancela la reserva, o el paseador asignado se retira.
    2. El sistema evalúa si faltan 30 minutos o menos para el inicio.
    3. Si el dueño cancela, la reserva pasa a Cancelada. Si se retira el paseador, vuelve a Pendiente y se libera su cupo.
    4. Si la cancelación es tardía, el sistema registra una penalidad a quien canceló (15 % de la tarifa).
    5. El sistema registra el evento.
- **Flujos alternativos / errores:**
    - a) Turno ya iniciado o reserva en estado final: error de transición inválida.
    - b) Usuario que no es el dueño ni el paseador asignado: error 403.
    - c) Si la reserva vuelve a Pendiente con poco tiempo restante, expira en la siguiente consulta.
- **Postcondición:** La reserva cambia de estado y, si correspondía, queda una penalidad registrada (no se cobra).

### CU08 – Consultar domicilio del dueño

- **Actor:** Paseador
- **Requerimientos:** RF29
- **Precondiciones:** La reserva está Aceptada y asignada al paseador.
- **Flujo principal:**
    1. El paseador solicita el domicilio de la reserva.
    2. El sistema verifica que sea el paseador asignado y que la reserva esté Aceptada.
    3. El sistema devuelve calle, número y barrio.
- **Flujos alternativos / errores:**
    - a) Paseador no asignado: error 403.
    - b) Reserva en otro estado: error 409.
- **Postcondición:** El paseador conoce la dirección para realizar el paseo.

### CU09 – Finalizar paseo

- **Actor:** Paseador
- **Requerimientos:** RF26, RF27, RF28
- **Precondiciones:** La reserva está Aceptada, asignada al paseador, y su turno ya comenzó.
- **Flujo principal:**
    1. El paseador registra la devolución de la mascota.
    2. El sistema guarda el instante de devolución y lo compara con el fin del turno para marcar la devolución tardía.
    3. El sistema pasa la reserva a Finalizada y registra el evento.
- **Flujos alternativos / errores:**
    - a) Usuario distinto del paseador asignado: error 403.
    - b) Reserva no aceptada o turno no iniciado: error de transición inválida.
- **Postcondición:** La reserva queda Finalizada y habilitada para el pago.

### CU10 – Pagar el paseo

- **Actor:** Dueño (paga) y Paseador (confirma el pago)
- **Requerimientos:** RF35, RF36, RF37, RF38
- **Precondiciones:** La reserva está Finalizada y todavía no tiene un pago.
- **Flujo principal:**
    1. El dueño elige el método de pago (efectivo, transferencia o tarjeta; la tarjeta requiere un número de prueba que no se guarda).
    2. El sistema crea el pago con el monto de la tarifa y lo procesa con el procesador del método elegido.
    3. La tarjeta queda aprobada o rechazada según el número de prueba; el efectivo y la transferencia quedan Pendientes.
    4. El paseador confirma el efectivo o la transferencia para aprobarlo o rechazarlo.
- **Flujos alternativos / errores:**
    - a) Reserva no finalizada: error 409.
    - b) Reserva ya pagada: error de conflicto.
    - c) Quien paga no es el dueño de la reserva: error 403.
- **Postcondición:** Queda registrado un pago asociado a la reserva. No hay cobro real.

# 8. Especificación del sistema

## 8.1 Estados de la reserva

- **Pendiente:** espera ser aceptada. Es el estado inicial y también al que vuelve la reserva si el paseador retira su aceptación.

- **Aceptada:** un paseador la tomó y quedó asignado. El dueño puede cancelarla, el paseador puede retirarse o finalizarla.

- **Cancelada:** el dueño la canceló. Estado final.

- **Expirada:** ningún paseador la aceptó antes del límite. Estado final.

- **Finalizada:** el paseador registró la devolución de la mascota. Estado final.

Los estados finales no admiten ninguna acción posterior. El estado se guarda en la base como enum (EstadoReserva) y de él se obtiene el objeto estado (patrón State) que aplica las reglas.

## 8.2 Transiciones de estado

| **Estado origen** | **Acción**         | **Actor** | **RF** | **Estado** **destino**                         |
|-------------------|--------------------|-----------|--------|------------------------------------------------|
| Pendiente         | Aceptar            | Paseador  | RF20   | Aceptada                                       |
| Pendiente         | Cancelar reserva   | Dueño     | RF23   | Cancelada (sin penalidad)                      |
| Pendiente         | Expirar            | Sistema   | RF25   | Expirada                                       |
| Aceptada          | Cancelar reserva   | Dueño     | RF23   | Cancelada (penalidad si faltan 30 min o menos) |
| Aceptada          | Retirar aceptación | Paseador  | RF24   | Pendiente (penalidad si faltan 30 min o menos) |
| Aceptada          | Finalizar          | Paseador  | RF26   | Finalizada                                     |

## 8.3 Reglas de negocio

- **Roles y datos propios:** un solo rol por cuenta. Cada usuario solo accede a sus recursos y el dueño de mascotas y reservas se toma del token.

- **Crear reserva:** turno dentro del mes actual, entre las 8:00 y las 20:00, con al menos 2 horas de anticipación, mascota propia y antirrábica vigente (1 año desde su aplicación) a la fecha del turno.

- **Aceptar reserva:** se rechaza si ya fue tomada, expiró o fue cancelada; si ese paseador ya canceló su aceptación sobre ella; o si superaría el tope de mascotas por turno.

- **Cancelar:** sin penalidad si está pendiente o si faltan más de 30 minutos. Con 30 minutos o menos se registra la penalidad. Con el turno iniciado no se puede cancelar.

- **Retirar aceptación:** misma regla de penalidad. La reserva vuelve a Pendiente, pierde su paseador y se libera el cupo. La penalidad se asigna al paseador que se retiró.

- **Expirar:** una reserva pendiente se marca como expirada, al momento de la siguiente consulta, cuando el tiempo restante para el inicio es menor al límite configurado (30 minutos).

- **Finalizar:** solo el paseador asignado, sobre una reserva aceptada cuyo turno ya comenzó. La marca de devolución tardía es informativa.

- **Domicilio:** calle, número y barrio se copian al crear la reserva y no se editan. Cambiar el domicilio del usuario no altera reservas existentes.

- **Bajas:** un usuario con reservas pendientes o aceptadas no puede darse de baja. Un usuario inactivo no inicia sesión ni aparece en listados, y su historial se conserva. Las mascotas con reservas pendientes o aceptadas no pueden eliminarse.

- **Pagos:** solo se puede pagar una reserva Finalizada, y no puede tener dos pagos pendientes o aprobados a la vez (si un pago se rechaza, se puede volver a intentar). El efectivo y la transferencia quedan pendientes hasta que el paseador los confirma; la tarjeta se aprueba o rechaza en el momento.

- **Penalidades:** se crean solo cuando se infringe la regla, van a quien infringe y en el MVP solo se registran.

## 8.4 Parámetros de configuración (valores del código)

| **Parámetro**                                 | **Valor**                   | **Dónde se define** |
|-----------------------------------------------|-----------------------------|---------------------|
| Tope de mascotas por paseador y turno         | 4                           | config.py           |
| Horario de turnos                             | 8:00 a 20:00                | config.py           |
| Anticipación mínima para crear una reserva    | 2 horas                     | config.py           |
| Expiración de reserva no aceptada             | 30 minutos antes del inicio | config.py           |
| Límite de cancelación sin penalidad           | 30 minutos antes del inicio | config.py           |
| Precio base                                   | \$8.000                     | config.py           |
| Factor de tamaño (Pequeño / Mediano / Grande) | 1,10 / 1,20 / 1,30          | config.py           |
| Porcentaje de comisión de la plataforma       | 15 %                        | config.py           |
| Porcentaje de penalidad (dueño y paseador)    | 15 % de la tarifa           | config.py           |
| Edad mínima / máxima dueño / máxima paseador  | 18 / 99 / 65 años           | settings.py         |
| Vencimiento del token JWT                     | 30 minutos                  | settings.py         |
| Barrios válidos                               | 48 barrios de CABA (enum)   | usuarios/enums.py   |

## 8.5 Cálculos

| **Cálculo**                | **Fórmula**                    | **Ejemplo (mascota mediana)** |
|----------------------------|--------------------------------|-------------------------------|
| Tarifa                     | Precio base x factor de tamaño | 8.000 x 1,20 = \$9.600        |
| Comisión                   | Tarifa x 15 %                  | \$1.440                       |
| Ganancia neta del paseador | Tarifa − comisión              | \$8.160                       |
| Penalidad                  | Tarifa x 15 %                  | \$1.440                       |

Tarifas por tamaño: pequeño \$8.800, mediano \$9.600, grande \$10.400.

# 9. Decisiones de diseño y patrones

- **State:** el comportamiento de la reserva depende de su estado. El enum EstadoReserva se persiste y de él se elige el objeto estado (PendienteState, AceptadaState, etc.) que aplica las reglas de transición.

- **Strategy + Factory simple (pagos):** cada método de pago tiene su procesador, que se elige según el método. Agregar un método (por ejemplo una pasarela real) implica un valor nuevo en el enum y un procesador nuevo, sin tocar el resto.

- **Expirar al consultar:** se eligió evaluar al consultar y no un proceso periódico, para evitar infraestructura extra.

- **Arquitectura en capas:** router, servicio y repositorio por módulo. Los servicios aplican las reglas y lanzan excepciones; además, un manejador único las traduce a códigos HTTP.

- **Tiempo inyectado:** el parámetro ahora se recibe desde afuera para probar reglas de tiempo con fechas fijas.

- **Historial:** cada cambio de estado crea un EventoReserva en la misma transacción. Lo crea el servicio y guarda al actor, lo que permite impedir que un paseador reacepte una reserva que canceló.

- **Datos derivados y copias:** el dueño de una reserva se obtiene desde la mascota; el domicilio y la tarifa se copian al crear la reserva.

## Despliegue

La API se empaqueta en un contenedor Docker, se configura por variables de entorno (SECRET_KEY, DATABASE_URL) y está desplegada en Render. La documentación interactiva queda en /docs. Actualmente se usa SQLite; como el servicio lee DATABASE_URL, migrar a PostgreSQL no requiere cambios en el código de negocio y es la mejora recomendada para que los datos persistan entre despliegues.

# 10. Visión del producto (trabajo futuro)

- **Notificaciones:** avisos automáticos ante cambios de estado de la reserva con patrón Observer, reutilizando EventoReserva, con un endpoint GET /notificaciones.

- **Mascotas:** consulta de los datos de la mascota por el paseador, con foto obligatoria y carnet de vacunación adjunto.

- **Usuarios:** foto de perfil obligatoria para el paseador.

- **Reservas:** descarte de reservas que no interesan al paseador, filtro por zona, tolerancia de devolución de 15 minutos, excepciones a la penalidad por clima adverso (API externa) o mutuo acuerdo, y sanciones por devoluciones tardías o cancelaciones reiteradas.

- **Pagos:** integración con una pasarela real (por ejemplo Mercado Pago) y cobro efectivo de penalidades.

- **Mapeo, reportes e historial:** puntos GPS del paseo (ruta, distancia, calles), reporte de inconformidad de identidad e historial de compañeros de paseo.

- **Calidad:** calificación bidireccional de 1 a 5 estrellas.

- **Extensibilidad del servicio:** tipos de paseo (solo, grupal, grupo reducido).

- **Infraestructura y front:** base de datos PostgreSQL, y un frontend más completo sobre la API.
