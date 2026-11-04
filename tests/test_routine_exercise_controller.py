from datetime import date


def _crear_rutina(client, user_id=3):
    """Crea una rutina para el cliente (id 3) y devuelve su id."""
    response = client.post(
        "/routines",
        json={"user_id": user_id, "date_generated": date.today().isoformat()},
    )
    assert response.status_code == 201
    return response.json()["id"]


def _crear_ejercicio(client, nombre):
    """Crea un ejercicio y devuelve su id (el ejercicio 1 ya viene sembrado)."""
    response = client.post(
        "/exercises",
        json={"name": nombre, "description": "Ejercicio de prueba", "muscular_group": "pecho"},
    )
    assert response.status_code == 201
    return response.json()["id"]


def _payload(exercise_id=1, day="lunes", sets=3, repetitions="10", position=1, rest=60):
    return {
        "exercise_id": exercise_id,
        "day": day,
        "sets": sets,
        "repetitions": repetitions,
        "position": position,
        "rest": rest,
    }


def test_create_routine_exercise(client, auth_profesor):
    # 1. Creamos la rutina y agregamos el ejercicio sembrado (id 1) un lunes
    rutina = _crear_rutina(client)
    response = client.post(f"/routines/{rutina}/exercises", json=_payload(), headers=auth_profesor)

    # 2. Comprobamos que se creó con los datos enviados
    assert response.status_code == 201
    assert response.json()["routine_id"] == rutina
    assert response.json()["exercise_id"] == 1
    assert response.json()["day"] == "lunes"
    assert response.json()["position"] == 1


def test_create_routine_exercise_cliente_forbidden(client, auth_cliente):
    # 1. El cliente intenta agregar un ejercicio a una rutina
    rutina = _crear_rutina(client)
    response = client.post(f"/routines/{rutina}/exercises", json=_payload(), headers=auth_cliente)

    # 2. Comprobamos que la escritura es solo de profesor/admin (403)
    assert response.status_code == 403


def test_create_routine_not_found(client):
    # 1. Intentamos agregar un ejercicio a una rutina inexistente (id 999)
    response = client.post("/routines/999/exercises", json=_payload())

    # 2. Comprobamos que devuelve 404
    assert response.status_code == 404
    assert response.json()["detail"] == "Routine not found"


def test_create_exercise_not_found(client):
    # 1. Intentamos agregar un ejercicio inexistente (id 999)
    rutina = _crear_rutina(client)
    response = client.post(f"/routines/{rutina}/exercises", json=_payload(exercise_id=999))

    # 2. Comprobamos que devuelve 404
    assert response.status_code == 404
    assert response.json()["detail"] == "Exercise not found"


def test_create_ejercicio_repetido(client):
    # 1. Agregamos el ejercicio 1 el lunes
    rutina = _crear_rutina(client)
    client.post(f"/routines/{rutina}/exercises", json=_payload())

    # 2. Intentamos agregar el mismo ejercicio el mismo día (otra posición)
    response = client.post(f"/routines/{rutina}/exercises", json=_payload(position=2))

    # 3. Comprobamos que devuelve 409
    assert response.status_code == 409
    assert "ya existe" in response.json()["detail"]


def test_create_posicion_ocupada(client):
    # 1. Agregamos el ejercicio 1 en la posición 1 del lunes
    rutina = _crear_rutina(client)
    ejercicio2 = _crear_ejercicio(client, "Remo con barra")
    client.post(f"/routines/{rutina}/exercises", json=_payload())

    # 2. Intentamos poner otro ejercicio en la misma posición y día
    response = client.post(f"/routines/{rutina}/exercises", json=_payload(exercise_id=ejercicio2))

    # 3. Comprobamos que devuelve 409
    assert response.status_code == 409
    assert "posición" in response.json()["detail"]


def test_create_mismo_ejercicio_otro_dia(client):
    # 1. Agregamos el ejercicio 1 el lunes
    rutina = _crear_rutina(client)
    client.post(f"/routines/{rutina}/exercises", json=_payload())

    # 2. Lo agregamos también el martes con la misma posición
    response = client.post(f"/routines/{rutina}/exercises", json=_payload(day="martes"))

    # 3. Comprobamos que es válido: el chequeo es por día
    assert response.status_code == 201
    assert response.json()["day"] == "martes"


def test_create_dia_invalido(client):
    # 1. Enviamos el día en mayúscula (el enum usa minúscula y sin acento)
    rutina = _crear_rutina(client)
    response = client.post(f"/routines/{rutina}/exercises", json=_payload(day="LUNES"))

    # 2. Comprobamos que el backend lo rechaza por validación (422)
    assert response.status_code == 422


def test_create_datos_invalidos(client):
    # 1. Enviamos sets en 0, lo que no es válido
    rutina = _crear_rutina(client)
    response = client.post(f"/routines/{rutina}/exercises", json=_payload(sets=0))

    # 2. Comprobamos que el backend lo rechaza por validación (422)
    assert response.status_code == 422


def test_get_routine_exercises(client, auth_cliente):
    # 1. Creamos una rutina con dos ejercicios
    rutina = _crear_rutina(client)
    ejercicio2 = _crear_ejercicio(client, "Remo con barra")
    client.post(f"/routines/{rutina}/exercises", json=_payload())
    client.post(f"/routines/{rutina}/exercises", json=_payload(exercise_id=ejercicio2, position=2))

    # 2. Listamos con token de cliente: la lectura es para cualquier autenticado
    response = client.get(f"/routines/{rutina}/exercises", headers=auth_cliente)

    # 3. Comprobamos que devuelve los dos renglones
    assert response.status_code == 200
    assert len(response.json()) == 2


def test_get_routine_exercises_vacia(client):
    # 1. Listamos los ejercicios de una rutina recién creada
    rutina = _crear_rutina(client)
    response = client.get(f"/routines/{rutina}/exercises")

    # 2. Comprobamos que devuelve una lista vacía
    assert response.status_code == 200
    assert response.json() == []


def test_get_routine_exercises_not_found(client):
    # 1. Listamos los ejercicios de una rutina inexistente (id 999)
    response = client.get("/routines/999/exercises")

    # 2. Comprobamos que devuelve 404
    assert response.status_code == 404
    assert response.json()["detail"] == "Routine not found"


def test_update_routine_exercise(client):
    # 1. Creamos un renglón
    rutina = _crear_rutina(client)
    creado = client.post(f"/routines/{rutina}/exercises", json=_payload())

    # 2. Actualizamos series y repeticiones
    response = client.patch(
        f"/routines/{rutina}/exercises/{creado.json()['id']}",
        json={"sets": 5, "repetitions": "12"},
    )

    # 3. Comprobamos que se actualizó
    assert response.status_code == 200
    assert response.json()["sets"] == 5
    assert response.json()["repetitions"] == "12"


def test_update_posicion_ocupada(client):
    # 1. Creamos dos renglones en el lunes, posiciones 1 y 2
    rutina = _crear_rutina(client)
    ejercicio2 = _crear_ejercicio(client, "Remo con barra")
    client.post(f"/routines/{rutina}/exercises", json=_payload())
    segundo = client.post(
        f"/routines/{rutina}/exercises", json=_payload(exercise_id=ejercicio2, position=2)
    )

    # 2. Intentamos mover el segundo a la posición 1
    response = client.patch(
        f"/routines/{rutina}/exercises/{segundo.json()['id']}", json={"position": 1}
    )

    # 3. Comprobamos que devuelve 409
    assert response.status_code == 409
    assert "posición" in response.json()["detail"]


def test_update_re_id_de_otra_rutina(client):
    # 1. Creamos un renglón en la rutina 1
    rutina = _crear_rutina(client)
    otra_rutina = _crear_rutina(client)
    creado = client.post(f"/routines/{rutina}/exercises", json=_payload())

    # 2. Intentamos actualizarlo usando el id de la otra rutina
    response = client.patch(
        f"/routines/{otra_rutina}/exercises/{creado.json()['id']}", json={"sets": 5}
    )

    # 3. Comprobamos que valida la pertenencia (404)
    assert response.status_code == 404
    assert response.json()["detail"] == "Routine exercise not found"


def test_update_routine_exercise_cliente_forbidden(client, auth_cliente):
    # 1. Creamos un renglón
    rutina = _crear_rutina(client)
    creado = client.post(f"/routines/{rutina}/exercises", json=_payload())

    # 2. El cliente intenta actualizarlo
    response = client.patch(
        f"/routines/{rutina}/exercises/{creado.json()['id']}",
        json={"sets": 5},
        headers=auth_cliente,
    )

    # 3. Comprobamos que devuelve 403
    assert response.status_code == 403


def test_delete_routine_exercise(client):
    # 1. Creamos un renglón
    rutina = _crear_rutina(client)
    creado = client.post(f"/routines/{rutina}/exercises", json=_payload())

    # 2. Lo eliminamos
    response = client.delete(f"/routines/{rutina}/exercises/{creado.json()['id']}")

    # 3. Comprobamos que devuelve 204 y que ya no está en el listado
    assert response.status_code == 204
    assert client.get(f"/routines/{rutina}/exercises").json() == []


def test_delete_renumera_posiciones(client):
    # 1. Creamos tres renglones en el lunes, posiciones 1, 2 y 3
    rutina = _crear_rutina(client)
    ejercicio2 = _crear_ejercicio(client, "Remo con barra")
    ejercicio3 = _crear_ejercicio(client, "Sentadilla")
    client.post(f"/routines/{rutina}/exercises", json=_payload())
    del_medio = client.post(
        f"/routines/{rutina}/exercises", json=_payload(exercise_id=ejercicio2, position=2)
    )
    client.post(
        f"/routines/{rutina}/exercises", json=_payload(exercise_id=ejercicio3, position=3)
    )

    # 2. Borramos el del medio
    client.delete(f"/routines/{rutina}/exercises/{del_medio.json()['id']}")

    # 3. Comprobamos que las posiciones quedan 1 y 2, sin huecos
    response = client.get(f"/routines/{rutina}/exercises")
    assert [renglon["position"] for renglon in response.json()] == [1, 2]


def test_delete_re_id_de_otra_rutina(client):
    # 1. Creamos un renglón en la rutina 1
    rutina = _crear_rutina(client)
    otra_rutina = _crear_rutina(client)
    creado = client.post(f"/routines/{rutina}/exercises", json=_payload())

    # 2. Intentamos borrarlo usando el id de la otra rutina
    response = client.delete(f"/routines/{otra_rutina}/exercises/{creado.json()['id']}")

    # 3. Comprobamos que valida la pertenencia (404)
    assert response.status_code == 404
    assert response.json()["detail"] == "Routine exercise not found"


def test_delete_routine_exercise_not_found(client):
    # 1. Intentamos borrar un renglón inexistente (id 999)
    rutina = _crear_rutina(client)
    response = client.delete(f"/routines/{rutina}/exercises/999")

    # 2. Comprobamos que devuelve 404
    assert response.status_code == 404
