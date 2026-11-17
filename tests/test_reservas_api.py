from datetime import datetime

import pytest
from fastapi.testclient import TestClient

from config import MAX_PERROS_SIMULTANEOS
from paseos.app import app
from paseos.core.dependencies import get_ahora
from fastapi import status

@pytest.fixture
def fijar_ahora():
    """Permite controlar el reloj de la API en cada paso del test."""

    def _set(instante: datetime):
        app.dependency_overrides[get_ahora] = lambda: instante

    yield _set
    app.dependency_overrides.pop(get_ahora, None)


def _registrar_y_loguear(client: TestClient, payload: dict) -> dict:
    """Registra un usuario, inicia sesión y devuelve los headers con el Bearer token."""
    res_reg = client.post('/auth/registro', json=payload)
    assert res_reg.status_code == status.HTTP_201_CREATED, res_reg.text

    res_login = client.post(
        '/auth/login',
        data={'username': payload['email'], 'password': payload['password']},
    )
    assert res_login.status_code == status.HTTP_200_OK, res_login.text
    token = res_login.json()['access_token']
    return {'Authorization': f'Bearer {token}'}


def _crear_mascota(
    client: TestClient, headers_dueno: dict, nombre: str
) -> int:
    """Helper para crear una mascota válida con vacuna antirrábica al día."""
    res = client.post(
        '/mascotas',
        headers=headers_dueno,
        json={
            'nombre': nombre,
            'fecha_nacimiento': '2022-03-10',
            'tamaño': 'MEDIANO',
            'raza': 'Mestizo',
            'fecha_antirrabica': '2026-01-15',
        },
    )
    assert res.status_code == status.HTTP_201_CREATED, res.text
    return res.json()['id']


@pytest.fixture
def escenario(client: TestClient, fijar_ahora):
    """Crea un dueño con mascota vacunada y un paseador listos para operar."""
    fijar_ahora(datetime(2026, 5, 10, 9, 0))

    headers_dueno = _registrar_y_loguear(
        client,
        {
            'email': 'dueno@test.com',
            'password': 'hackeable456',
            'nombre': 'ludmila dueña',
            'dni': '30111222',
            'fecha_nacimiento': '1990-05-15',
            'calle': 'Av. Santa Fe',
            'numero': '1234',
            'barrio': 'PALERMO',
            'rol': 'DUENO',
        },
    )

    headers_paseador = _registrar_y_loguear(
        client,
        {
            'email': 'paseador@test.com',
            'password': 'hackeable456',
            'nombre': 'florencia paseadora',
            'dni': '32333444',
            'fecha_nacimiento': '1995-08-20',
            'calle': 'Cabildo',
            'numero': '500',
            'barrio': 'BELGRANO',
            'rol': 'PASEADOR',
        },
    )

    mascota_id = _crear_mascota(client, headers_dueno, 'Firulais')

    return {
        'dueno': headers_dueno,
        'paseador': headers_paseador,
        'mascota_id': mascota_id,
    }


def test_crear_reserva_y_privacidad_domicilio(
    client: TestClient, escenario, fijar_ahora
):
    fijar_ahora(datetime(2026, 5, 10, 10, 0))

    # 1. Dueño crea reserva para hoy a las 14:00 (cumple >= 2hs anticipación)
    res = client.post(
        '/reservas',
        headers=escenario['dueno'],
        json={
            'mascota_id': escenario['mascota_id'],
            'fecha': '2026-05-10',
            'hora_inicio': '14:00:00',
            'hora_fin': '15:00:00',
        },
    )
    assert res.status_code == status.HTTP_201_CREATED, res.text
    data = res.json()
    reserva_id = data['id']
    assert data['estado'] == 'PENDIENTE'
    assert data['calle'] == 'Av. Santa Fe'
    assert 'comision' not in data  # El dueño no ve comisión

    # 2. Paseador lista pendientes: ve barrio y comisión, pero NO calle ni número
    res_pend = client.get(
        '/reservas/pendientes?barrio=PALERMO', headers=escenario['paseador']
    )
    assert res_pend.status_code == status.HTTP_200_OK
    pendientes = res_pend.json()
    assert len(pendientes) == 1
    assert pendientes[0]['barrio'] == 'PALERMO'
    assert 'comision' in pendientes[0]
    assert 'calle' not in pendientes[0]
    assert 'numero' not in pendientes[0]

    # 3. Paseador intenta ver domicilio mientras sigue PENDIENTE -> 403 Forbidden
    res_dom_antes = client.get(f"/reservas/{reserva_id}/domicilio", headers=escenario["paseador"])
    assert res_dom_antes.status_code == status.HTTP_403_FORBIDDEN

    # 4. Paseador acepta la reserva -> ahora sí puede ver calle y número
    res_aceptar = client.post(
        f'/reservas/{reserva_id}/aceptar', headers=escenario['paseador']
    )
    assert res_aceptar.status_code == status.HTTP_200_OK
    assert res_aceptar.json()['estado'] == 'ACEPTADA'

    res_dom_despues = client.get(
        f'/reservas/{reserva_id}/domicilio', headers=escenario['paseador']
    )
    assert res_dom_despues.status_code == status.HTTP_200_OK
    assert res_dom_despues.json() == {
        'calle': 'Av. Santa Fe',
        'numero': '1234',
        'barrio': 'PALERMO',
    }


def test_baja_usuario_bloqueada_con_reserva_activa(
    client: TestClient, escenario, fijar_ahora
):
    fijar_ahora(datetime(2026, 5, 10, 10, 0))

    res = client.post(
        '/reservas',
        headers=escenario['dueno'],
        json={
            'mascota_id': escenario['mascota_id'],
            'fecha': '2026-05-10',
            'hora_inicio': '14:00:00',
            'hora_fin': '15:00:00',
        },
    )
    reserva_id = res.json()['id']

    # Intentar darse de baja con reserva PENDIENTE debe dar 409 Conflict
    res_baja = client.delete('/usuarios/me', headers=escenario['dueno'])
    assert res_baja.status_code == status.HTTP_409_CONFLICT

    # Cancela la reserva y ahora sí puede darse de baja (204)
    client.post(f'/reservas/{reserva_id}/cancelar', headers=escenario['dueno'])
    res_baja_ok = client.delete('/usuarios/me', headers=escenario['dueno'])
    assert res_baja_ok.status_code == status.HTTP_204_NO_CONTENT


def test_cancelacion_tardia_genera_penalidad(
    client: TestClient, escenario, fijar_ahora
):
    # Reserva a las 14:00
    fijar_ahora(datetime(2026, 5, 10, 10, 0))
    res = client.post(
        '/reservas',
        headers=escenario['dueno'],
        json={
            'mascota_id': escenario['mascota_id'],
            'fecha': '2026-05-10',
            'hora_inicio': '14:00:00',
            'hora_fin': '15:00:00',
        },
    )
    reserva_id = res.json()['id']

    # Paseador acepta a las 11:00
    fijar_ahora(datetime(2026, 5, 10, 11, 0))
    client.post(
        f'/reservas/{reserva_id}/aceptar', headers=escenario['paseador']
    )

    # Paseador retira aceptación a las 13:45 (faltan 15 min -> < 30 min -> cancelación tardía)
    fijar_ahora(datetime(2026, 5, 10, 13, 45))
    res_retirar = client.post(
        f'/reservas/{reserva_id}/retirar-aceptacion',
        headers=escenario['paseador'],
    )
    assert res_retirar.status_code == status.HTTP_200_OK
    assert res_retirar.json()['estado'] == 'PENDIENTE'

    # Verificar que se registró la penalidad al paseador
    res_pen = client.get(
        '/reservas/penalidades/mias', headers=escenario['paseador']
    )
    assert res_pen.status_code == status.HTTP_200_OK
    penalidades = res_pen.json()
    assert len(penalidades) == 1
    assert penalidades[0]['motivo'] == 'CANCELACION_PASEADOR'
    assert float(penalidades[0]['monto']) > 0

    # El mismo paseador intenta volver a aceptarla -> 409 Conflict
    res_reaceptar = client.post(
        f'/reservas/{reserva_id}/aceptar', headers=escenario['paseador']
    )
    assert res_reaceptar.status_code == status.HTTP_409_CONFLICT


def test_expiracion_automatica_al_consultar(
    client: TestClient, escenario, fijar_ahora
):
    # Crea reserva a las 10:00 para las 14:00
    fijar_ahora(datetime(2026, 5, 10, 10, 0))
    res = client.post(
        '/reservas',
        headers=escenario['dueno'],
        json={
            'mascota_id': escenario['mascota_id'],
            'fecha': '2026-05-10',
            'hora_inicio': '14:00:00',
            'hora_fin': '15:00:00',
        },
    )
    reserva_id = res.json()['id']

    # Adelantamos el reloj a las 13:55 (dentro del margen de expiración) y consultamos pendientes
    fijar_ahora(datetime(2026, 5, 10, 13, 55))
    res_pend = client.get(
        '/reservas/pendientes', headers=escenario['paseador']
    )
    assert res_pend.status_code == status.HTTP_200_OK
    assert res_pend.json() == []

    # El dueño consulta sus reservas y confirma que figura EXPIRADA
    res_mias = client.get('/reservas/mias', headers=escenario['dueno'])
    assert res_mias.status_code == status.HTTP_200_OK
    assert res_mias.json()[0]['id'] == reserva_id
    assert res_mias.json()[0]['estado'] == 'EXPIRADA'


def test_flujo_finalizacion_y_devolucion_tardia(
    client: TestClient, escenario, fijar_ahora
):
    fijar_ahora(datetime(2026, 5, 10, 10, 0))
    res = client.post(
        '/reservas',
        headers=escenario['dueno'],
        json={
            'mascota_id': escenario['mascota_id'],
            'fecha': '2026-05-10',
            'hora_inicio': '14:00:00',
            'hora_fin': '15:00:00',
        },
    )
    reserva_id = res.json()['id']

    client.post(
        f'/reservas/{reserva_id}/aceptar', headers=escenario['paseador']
    )

    # Finaliza a las 15:20 (20 minutos después de hora_fin)
    fijar_ahora(datetime(2026, 5, 10, 15, 20))
    res_fin = client.post(
        f'/reservas/{reserva_id}/finalizar', headers=escenario['paseador']
    )
    assert res_fin.status_code == status.HTTP_200_OK
    body = res_fin.json()
    assert body['estado'] == 'FINALIZADA'
    assert body['devolucion_tardia'] is True


def test_aceptar_hasta_maximo_perros_simultaneos_no_falla(
    client: TestClient, escenario, fijar_ahora
):
    """El paseador puede aceptar hasta MAX_PERROS_SIMULTANEOS en el mismo turno sin error;
    recién al superar el límite devuelve 409 Conflict.
    """
    fijar_ahora(datetime(2026, 5, 10, 10, 0))

    reservas_ids = []
    for i in range(MAX_PERROS_SIMULTANEOS + 1):
        mascota_id = _crear_mascota(client, escenario['dueno'], f'Perro_{i}')
        res = client.post(
            '/reservas',
            headers=escenario['dueno'],
            json={
                'mascota_id': mascota_id,
                'fecha': '2026-05-10',
                'hora_inicio': '14:00:00',
                'hora_fin': '15:00:00',
            },
        )
        assert res.status_code == status.HTTP_201_CREATED, res.text
        reservas_ids.append(res.json()['id'])

    # Aceptar exactamente hasta el límite permitido NO falla
    for reserva_id in reservas_ids[:MAX_PERROS_SIMULTANEOS]:
        res_ok = client.post(
            f'/reservas/{reserva_id}/aceptar',
            headers=escenario['paseador'],
        )
        assert res_ok.status_code == status.HTTP_200_OK, res_ok.text
        assert res_ok.json()['estado'] == 'ACEPTADA'

    # La reserva extra (sobreturno por encima del tope) sí debe rechazarse con 409
    res_exceso = client.post(
        f'/reservas/{reservas_ids[-1]}/aceptar',
        headers=escenario['paseador'],
    )
    assert res_exceso.status_code == status.HTTP_409_CONFLICT


#tests para terminar de verificar todo

def test_tope_perros_con_turnos_parcialmente_superpuestos(
    client: TestClient, escenario, fijar_ahora
):
    """Permite hasta MAX_PERROS_SIMULTANEOS turnos solapados y rechaza el 5to."""
    fijar_ahora(datetime(2026, 5, 10, 8, 0))

    horarios = [
        ("14:00:00", "15:00:00"),
        ("14:15:00", "15:15:00"),
        ("14:30:00", "15:30:00"),
        ("14:45:00", "15:45:00"),
    ]
    for i in range(MAX_PERROS_SIMULTANEOS):
        h_ini, h_fin = horarios[i % len(horarios)]
        mascota_id = _crear_mascota(client, escenario["dueno"], f"Solapado_{i}")
        res = client.post(
            "/reservas",
            headers=escenario["dueno"],
            json={
                "mascota_id": mascota_id,
                "fecha": "2026-05-10",
                "hora_inicio": h_ini,
                "hora_fin": h_fin,
            },
        )
        assert res.status_code == status.HTTP_201_CREATED, res.text

        res = client.post(
            f"/reservas/{res.json()['id']}/aceptar",
            headers=escenario["paseador"],
        )
        assert res.status_code == status.HTTP_200_OK, res.text

    # 5ta reserva superpuesta (14:50 a 15:50) -> debe fallar con 409
    mascota_extra = _crear_mascota(client, escenario["dueno"], "QuintoPerro")
    res = client.post(
        "/reservas",
        headers=escenario["dueno"],
        json={
            "mascota_id": mascota_extra,
            "fecha": "2026-05-10",
            "hora_inicio": "14:50:00",
            "hora_fin": "15:50:00",
        },
    )
    assert res.status_code == status.HTTP_201_CREATED

    res = client.post(
        f"/reservas/{res.json()['id']}/aceptar",
        headers=escenario["paseador"],
    )
    assert res.status_code == status.HTTP_409_CONFLICT

    # Turno contiguo exacto (15:00 a 16:00) no se pisa -> se permite
    mascota_contigua = _crear_mascota(client, escenario["dueno"], "Contiguo")
    res = client.post(
        "/reservas",
        headers=escenario["dueno"],
        json={
            "mascota_id": mascota_contigua,
            "fecha": "2026-05-10",
            "hora_inicio": "15:00:00",
            "hora_fin": "16:00:00",
        },
    )
    assert res.status_code == status.HTTP_201_CREATED

    res = client.post(
        f"/reservas/{res.json()['id']}/aceptar",
        headers=escenario["paseador"],
    )
    assert res.status_code == status.HTTP_200_OK


def test_errores_validacion_al_crear_reserva(
    client: TestClient, escenario, fijar_ahora
):
    fijar_ahora(datetime(2026, 5, 10, 10, 0))
    errores_regla = (
        status.HTTP_400_BAD_REQUEST,
        status.HTTP_409_CONFLICT,
        status.HTTP_422_UNPROCESSABLE_ENTITY,
    )

    # 1. Rol equivocado (paseador intentando crear reserva) -> 403
    res = client.post(
        "/reservas",
        headers=escenario["paseador"],
        json={
            "mascota_id": escenario["mascota_id"],
            "fecha": "2026-05-10",
            "hora_inicio": "14:00:00",
            "hora_fin": "15:00:00",
        },
    )
    assert res.status_code == status.HTTP_403_FORBIDDEN

    # 2. Mascota inexistente -> 404
    res = client.post(
        "/reservas",
        headers=escenario["dueno"],
        json={
            "mascota_id": 99999,
            "fecha": "2026-05-10",
            "hora_inicio": "14:00:00",
            "hora_fin": "15:00:00",
        },
    )
    assert res.status_code == status.HTTP_404_NOT_FOUND

    # 3. Mascota ajena (de otro dueño) -> 403
    otro_dueno = _registrar_y_loguear(
        client,
        {
            "email": "otro_dueno@test.com",
            "password": "Password123!",
            "nombre": "Ana Dueña",
            "dni": "31555666",
            "fecha_nacimiento": "1992-04-10",
            "calle": "Corrientes",
            "numero": "2000",
            "barrio": "ALMAGRO",
            "rol": "DUENO",
        },
    )
    res = client.post(
        "/reservas",
        headers=otro_dueno,
        json={
            "mascota_id": escenario["mascota_id"],
            "fecha": "2026-05-10",
            "hora_inicio": "14:00:00",
            "hora_fin": "15:00:00",
        },
    )
    assert res.status_code == status.HTTP_403_FORBIDDEN

    # 4. Mascota con antirrábica vencida (> 1 año)
    res = client.post(
        "/mascotas",
        headers=escenario["dueno"],
        json={
            "nombre": "Viejito",
            "fecha_nacimiento": "2018-01-01",
            "tamaño": "PEQUEÑO",
            "raza": "Caniche",
            "fecha_antirrabica": "2024-01-01",
        },
    )
    assert res.status_code == status.HTTP_201_CREATED

    res = client.post(
        "/reservas",
        headers=escenario["dueno"],
        json={
            "mascota_id": res.json()["id"],
            "fecha": "2026-05-10",
            "hora_inicio": "14:00:00",
            "hora_fin": "15:00:00",
        },
    )
    assert res.status_code in errores_regla

    # 5. Menos de 2 horas de anticipación (son las 10:00, turno a las 11:30)
    res = client.post(
        "/reservas",
        headers=escenario["dueno"],
        json={
            "mascota_id": escenario["mascota_id"],
            "fecha": "2026-05-10",
            "hora_inicio": "11:30:00",
            "hora_fin": "12:30:00",
        },
    )
    assert res.status_code in errores_regla

    # 6. Turno fuera de horario operativo (ej. 03:00 a 04:00)
    res = client.post(
        "/reservas",
        headers=escenario["dueno"],
        json={
            "mascota_id": escenario["mascota_id"],
            "fecha": "2026-05-11",
            "hora_inicio": "03:00:00",
            "hora_fin": "04:00:00",
        },
    )
    assert res.status_code in errores_regla

    # 7. Turno fuera de la ventana de 1 mes (ej. 45 días adelante)
    res = client.post(
        "/reservas",
        headers=escenario["dueno"],
        json={
            "mascota_id": escenario["mascota_id"],
            "fecha": "2026-07-01",
            "hora_inicio": "14:00:00",
            "hora_fin": "15:00:00",
        },
    )
    assert res.status_code in errores_regla


def test_privacidad_otro_paseador_y_filtros_listados(
    client: TestClient, escenario, fijar_ahora
):
    fijar_ahora(datetime(2026, 5, 10, 10, 0))

    # Dueño de PALERMO crea una reserva
    res = client.post(
        "/reservas",
        headers=escenario["dueno"],
        json={
            "mascota_id": escenario["mascota_id"],
            "fecha": "2026-05-10",
            "hora_inicio": "14:00:00",
            "hora_fin": "15:00:00",
        },
    )
    assert res.status_code == status.HTTP_201_CREATED
    reserva_id = res.json()["id"]

    # Filtro de /pendientes por otro barrio vs PALERMO
    res = client.get(
        "/reservas/pendientes?barrio=BELGRANO",
        headers=escenario["paseador"],
    )
    assert res.status_code == status.HTTP_200_OK
    assert res.json() == []

    res = client.get(
        "/reservas/pendientes?barrio=PALERMO",
        headers=escenario["paseador"],
    )
    assert res.status_code == status.HTTP_200_OK
    assert len(res.json()) == 1

    # Paseador 1 acepta la reserva
    res = client.post(
        f"/reservas/{reserva_id}/aceptar", headers=escenario["paseador"]
    )
    assert res.status_code == status.HTTP_200_OK

    # Otro paseador distinto intenta consultar el domicilio -> 403
    otro_paseador = _registrar_y_loguear(
        client,
        {
            "email": "otro_paseador@test.com",
            "password": "Password123!",
            "nombre": "Marcos Paseador",
            "dni": "33777888",
            "fecha_nacimiento": "1994-11-05",
            "calle": "Rivadavia",
            "numero": "4500",
            "barrio": "CABALLITO",
            "rol": "PASEADOR",
        },
    )
    res = client.get(
        f"/reservas/{reserva_id}/domicilio", headers=otro_paseador
    )
    assert res.status_code == status.HTTP_403_FORBIDDEN

    # /reservas/mias funciona tanto para el dueño como para el paseador
    res = client.get("/reservas/mias", headers=escenario["dueno"])
    assert res.status_code == status.HTTP_200_OK
    assert len(res.json()) == 1
    assert res.json()[0]["id"] == reserva_id

    res = client.get("/reservas/mias", headers=escenario["paseador"])
    assert res.status_code == status.HTTP_200_OK
    assert len(res.json()) == 1
    assert res.json()[0]["id"] == reserva_id

    res = client.get("/reservas/mias", headers=otro_paseador)
    assert res.status_code == status.HTTP_200_OK
    assert res.json() == []

