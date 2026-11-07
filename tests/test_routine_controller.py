from datetime import date


def _payload(user_id=3, generated_on=None, **extra):
    return {
        "user_id": user_id,
        "date_generated": (generated_on or date.today()).isoformat(),
        **extra,
    }


def _create_routine(client, user_id=3, **extra):
    """Crea una rutina como admin y devuelve el JSON de la respuesta."""
    response = client.post("/routines", json=_payload(user_id=user_id, **extra))
    assert response.status_code == 201
    return response.json()


def _add_exercise(client, routine_id):
    """Agrega el ejercicio sembrado (id 1) a la rutina."""
    response = client.post(
        f"/routines/{routine_id}/exercises",
        json={
            "exercise_id": 1,
            "day": "lunes",
            "sets": 3,
            "repetitions": "10",
            "position": 1,
            "rest": 60,
        },
    )
    assert response.status_code == 201


# ---------- POST /routines ----------

def test_create_routine(client):
    # 1. El admin crea una rutina para el cliente (id 3)
    response = client.post("/routines", json=_payload())

    # 2. Comprobamos que se creó con los datos enviados
    assert response.status_code == 201
    assert response.json()["id"] is not None
    assert response.json()["user_id"] == 3
    assert response.json()["date_generated"] == date.today().isoformat()


def test_create_routine_default_state(client):
    # 1. Creamos una rutina sin enviar "state"
    response = client.post("/routines", json=_payload())

    # 2. Comprobamos que queda activa por defecto
    assert response.status_code == 201
    assert response.json()["state"] is True


def test_create_routine_state_false(client):
    # 1. Creamos una rutina inactiva
    response = client.post("/routines", json=_payload(state=False))

    # 2. Comprobamos que respeta el valor enviado
    assert response.status_code == 201
    assert response.json()["state"] is False


def test_create_routine_professor(client, auth_profesor):
    # 1. El profesor crea una rutina
    response = client.post("/routines", json=_payload(), headers=auth_profesor)

    # 2. Comprobamos que tiene permiso (201)
    assert response.status_code == 201


def test_create_routine_customer_forbidden(client, auth_cliente):
    # 1. El cliente intenta crear una rutina
    response = client.post("/routines", json=_payload(), headers=auth_cliente)

    # 2. Comprobamos que la escritura es solo de profesor/admin (403)
    assert response.status_code == 403


def test_create_routine_invalid_token(client):
    # 1. Enviamos un token inválido
    response = client.post(
        "/routines", json=_payload(), headers={"Authorization": "Bearer token-invalido"}
    )

    # 2. Comprobamos que devuelve 401
    assert response.status_code == 401


def test_create_routine_user_not_found(client):
    # 1. Intentamos crear una rutina para un usuario inexistente (id 999)
    response = client.post("/routines", json=_payload(user_id=999))

    # 2. Comprobamos que devuelve 404
    assert response.status_code == 404
    assert response.json()["detail"] == "User not found"


def test_create_routine_invalid_user_id(client):
    # 1. Enviamos user_id en 0 (el schema exige > 0)
    response = client.post("/routines", json=_payload(user_id=0))

    # 2. Comprobamos que devuelve 422
    assert response.status_code == 422


def test_create_routine_invalid_date(client):
    # 1. Enviamos una fecha con formato inválido
    response = client.post("/routines", json={"user_id": 3, "date_generated": "no-es-fecha"})

    # 2. Comprobamos que devuelve 422
    assert response.status_code == 422


def test_create_routine_missing_fields(client):
    # 1. Enviamos un body sin date_generated
    response = client.post("/routines", json={"user_id": 3})

    # 2. Comprobamos que devuelve 422
    assert response.status_code == 422


# ---------- GET /routines ----------

def test_get_routines(client):
    # 1. Creamos dos rutinas
    _create_routine(client, user_id=3)
    _create_routine(client, user_id=2)

    # 2. Listamos como admin
    response = client.get("/routines")

    # 3. Comprobamos que devuelve las dos
    assert response.status_code == 200
    assert len(response.json()) == 2


def test_get_routines_empty(client):
    # 1. Listamos sin haber creado rutinas
    response = client.get("/routines")

    # 2. Comprobamos que devuelve una lista vacía
    assert response.status_code == 200
    assert response.json() == []


def test_get_routines_professor(client, auth_profesor):
    # 1. Creamos una rutina y listamos con token de profesor
    _create_routine(client)
    response = client.get("/routines", headers=auth_profesor)

    # 2. Comprobamos que el profesor puede listar
    assert response.status_code == 200
    assert len(response.json()) == 1


def test_get_routines_customer_forbidden(client, auth_cliente):
    # 1. El cliente intenta listar todas las rutinas
    response = client.get("/routines", headers=auth_cliente)

    # 2. Comprobamos que devuelve 403
    assert response.status_code == 403


# ---------- GET /routines/me ----------

def test_get_my_routines(client, auth_cliente):
    # 1. Creamos dos rutinas para el cliente y una para el profesor
    _create_routine(client, user_id=3)
    _create_routine(client, user_id=3)
    _create_routine(client, user_id=2)

    # 2. El cliente consulta sus rutinas
    response = client.get("/routines/me", headers=auth_cliente)

    # 3. Comprobamos que solo ve las suyas
    assert response.status_code == 200
    assert len(response.json()) == 2
    assert all(r["user_id"] == 3 for r in response.json())


def test_get_my_routines_empty(client, auth_cliente):
    # 1. El cliente consulta sin tener rutinas
    response = client.get("/routines/me", headers=auth_cliente)

    # 2. Comprobamos que devuelve una lista vacía
    assert response.status_code == 200
    assert response.json() == []


def test_get_my_routines_includes_exercises(client, auth_cliente):
    # 1. Creamos una rutina para el cliente con un ejercicio
    routine = _create_routine(client, user_id=3)
    _add_exercise(client, routine["id"])

    # 2. El cliente consulta sus rutinas
    response = client.get("/routines/me", headers=auth_cliente)

    # 3. Comprobamos que viene el detalle del ejercicio
    assert response.status_code == 200
    exercises = response.json()[0]["exercises"]
    assert len(exercises) == 1
    assert exercises[0]["day"] == "lunes"
    assert exercises[0]["exercise"]["name"] == "Press de banca"


def test_get_my_routines_invalid_token(client):
    # 1. Consultamos con un token inválido
    response = client.get("/routines/me", headers={"Authorization": "Bearer token-invalido"})

    # 2. Comprobamos que devuelve 401
    assert response.status_code == 401


# ---------- GET /routines/{id} ----------

def test_get_routine_by_id(client):
    # 1. Creamos una rutina
    routine = _create_routine(client)

    # 2. La consultamos por id
    response = client.get(f"/routines/{routine['id']}")

    # 3. Comprobamos que devuelve la misma rutina, sin ejercicios
    assert response.status_code == 200
    assert response.json()["id"] == routine["id"]
    assert response.json()["user_id"] == 3
    assert response.json()["exercises"] == []


def test_get_routine_by_id_with_exercises(client):
    # 1. Creamos una rutina y le agregamos un ejercicio
    routine = _create_routine(client)
    _add_exercise(client, routine["id"])

    # 2. La consultamos por id
    response = client.get(f"/routines/{routine['id']}")

    # 3. Comprobamos que incluye el ejercicio con su detalle
    assert response.status_code == 200
    assert len(response.json()["exercises"]) == 1
    assert response.json()["exercises"][0]["sets"] == 3
    assert response.json()["exercises"][0]["exercise"]["id"] == 1


def test_get_routine_by_id_customer(client, auth_cliente):
    # 1. Creamos una rutina y la consultamos con token de cliente
    routine = _create_routine(client)
    response = client.get(f"/routines/{routine['id']}", headers=auth_cliente)

    # 2. Comprobamos que la lectura es para cualquier autenticado
    assert response.status_code == 200


def test_get_routine_not_found(client):
    # 1. Consultamos una rutina inexistente (id 999)
    response = client.get("/routines/999")

    # 2. Comprobamos que devuelve 404
    assert response.status_code == 404
    assert response.json()["detail"] == "Routine not found"


# ---------- PATCH /routines/{id} ----------

def test_update_routine(client):
    # 1. Creamos una rutina
    routine = _create_routine(client)

    # 2. Cambiamos fecha y estado
    response = client.patch(
        f"/routines/{routine['id']}",
        json={"date_generated": "2026-01-15", "state": False},
    )

    # 3. Comprobamos que se actualizó
    assert response.status_code == 200
    assert response.json()["date_generated"] == "2026-01-15"
    assert response.json()["state"] is False


def test_update_routine_partial(client):
    # 1. Creamos una rutina
    routine = _create_routine(client)

    # 2. Actualizamos solo el estado
    response = client.patch(f"/routines/{routine['id']}", json={"state": False})

    # 3. Comprobamos que cambió el estado y la fecha quedó igual
    assert response.status_code == 200
    assert response.json()["state"] is False
    assert response.json()["date_generated"] == routine["date_generated"]


def test_update_routine_does_not_change_user(client):
    # 1. Creamos una rutina del cliente (id 3)
    routine = _create_routine(client, user_id=3)

    # 2. Intentamos reasignarla al profesor (user_id no está en RoutineUpdate)
    response = client.patch(f"/routines/{routine['id']}", json={"user_id": 2, "state": False})

    # 3. Comprobamos que el user_id se ignora
    assert response.status_code == 200
    assert response.json()["user_id"] == 3


def test_update_routine_professor(client, auth_profesor):
    # 1. Creamos una rutina y la actualizamos con token de profesor
    routine = _create_routine(client)
    response = client.patch(
        f"/routines/{routine['id']}", json={"state": False}, headers=auth_profesor
    )

    # 2. Comprobamos que tiene permiso
    assert response.status_code == 200


def test_update_routine_customer_forbidden(client, auth_cliente):
    # 1. El cliente intenta modificar una rutina
    routine = _create_routine(client)
    response = client.patch(
        f"/routines/{routine['id']}", json={"state": False}, headers=auth_cliente
    )

    # 2. Comprobamos que devuelve 403
    assert response.status_code == 403


def test_update_routine_not_found(client):
    # 1. Intentamos actualizar una rutina inexistente (id 999)
    response = client.patch("/routines/999", json={"state": False})

    # 2. Comprobamos que devuelve 404
    assert response.status_code == 404
    assert response.json()["detail"] == "Routine not found"


def test_update_routine_invalid_date(client):
    # 1. Enviamos una fecha con formato inválido
    routine = _create_routine(client)
    response = client.patch(f"/routines/{routine['id']}", json={"date_generated": "no-es-fecha"})

    # 2. Comprobamos que devuelve 422
    assert response.status_code == 422


# ---------- DELETE /routines/{id} ----------

def test_delete_routine(client):
    # 1. Creamos una rutina
    routine = _create_routine(client)

    # 2. La eliminamos
    response = client.delete(f"/routines/{routine['id']}")

    # 3. Comprobamos que devuelve 204 sin contenido y que ya no existe
    assert response.status_code == 204
    assert response.content == b""
    assert client.get(f"/routines/{routine['id']}").status_code == 404


def test_delete_routine_deletes_its_exercises(client):
    # 1. Creamos una rutina con un ejercicio
    routine = _create_routine(client)
    _add_exercise(client, routine["id"])

    # 2. Eliminamos la rutina
    response = client.delete(f"/routines/{routine['id']}")

    # 3. Comprobamos que se borró en cascada y el ejercicio del catálogo sigue existiendo
    assert response.status_code == 204
    assert client.get(f"/routines/{routine['id']}/exercises").status_code == 404
    assert client.get("/exercises/1").status_code == 200


def test_delete_routine_professor(client, auth_profesor):
    # 1. Creamos una rutina y la eliminamos con token de profesor
    routine = _create_routine(client)
    response = client.delete(f"/routines/{routine['id']}", headers=auth_profesor)

    # 2. Comprobamos que tiene permiso
    assert response.status_code == 204


def test_delete_routine_customer_forbidden(client, auth_cliente):
    # 1. El cliente intenta eliminar una rutina
    routine = _create_routine(client)
    response = client.delete(f"/routines/{routine['id']}", headers=auth_cliente)

    # 2. Comprobamos que devuelve 403 y la rutina sigue existiendo
    assert response.status_code == 403
    assert client.get(f"/routines/{routine['id']}").status_code == 200


def test_delete_routine_not_found(client):
    # 1. Intentamos eliminar una rutina inexistente (id 999)
    response = client.delete("/routines/999")

    # 2. Comprobamos que devuelve 404
    assert response.status_code == 404
    assert response.json()["detail"] == "Routine not found"