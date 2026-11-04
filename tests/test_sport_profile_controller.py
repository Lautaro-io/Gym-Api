def test_create_sport_profile(client):
    # 1. Preparamos los datos válidos que vamos a enviar
    payload = {
        "user_id": 1,
        "goal": "Definición muscular",
        "level": "Avanzado",
        "days_per_week": 5,
        "session_duration": 75,
        "age": 28,
        "injuries": None,
        "trainer_tracking": True,
    }

    # 2. Hacemos la petición POST al endpoint
    response = client.post("/sport-profiles", json=payload)

    # 3. Usamos 'assert' para comprobar que el programa hizo lo esperado
    assert response.status_code == 201
    assert response.json()["goal"] == "Definición muscular"
    assert response.json()["user_id"] == 1


def test_get_sport_profile(client):
    # 1. Hacemos la petición GET a un perfil deportivo existente (ej: id 1)
    response = client.get("/sport-profiles/1")

    # 2. Comprobamos el resultado automáticamente
    assert response.status_code == 200
    assert "user_id" in response.json()
    assert response.json()["goal"] == "Hipertrofia muscular"


def test_create_sport_profile_invalid_data(client):
    # 1. Intentamos crear un perfil con días por semana (> 7) y edad inválida (<= 10)
    payload = {
        "user_id": 1,
        "goal": "Bajar de peso",
        "level": "Principiante",
        "days_per_week": 9,
        "session_duration": -30,
        "age": 5,
        "injuries": None,
        "trainer_tracking": False,
    }

    # 2. Hacemos la petición POST al endpoint
    response = client.post("/sport-profiles", json=payload)

    # 3. Comprobamos que el backend rechaza la petición por datos inválidos (422)
    assert response.status_code == 422


def test_create_sport_profile_user_not_found(client):
    # 1. Intentamos crear un perfil deportivo para un usuario inexistente (ej: user_id 999)
    payload = {
        "user_id": 999,
        "goal": "Fuerza máxima",
        "level": "Avanzado",
        "days_per_week": 4,
        "session_duration": 60,
        "age": 30,
        "injuries": None,
        "trainer_tracking": False,
    }

    # 2. Hacemos la petición POST al endpoint
    response = client.post("/sport-profiles", json=payload)

    # 3. Comprobamos que devuelve 404 Not Found
    assert response.status_code == 404
    assert response.json()["detail"] == "User not found"


def test_get_sport_profile_not_found(client):
    # 1. Hacemos la petición GET a un perfil deportivo inexistente (ej: id 999)
    response = client.get("/sport-profiles/999")

    # 2. Comprobamos que devuelve 404 Not Found
    assert response.status_code == 404
    assert response.json()["detail"] == "Sport profile not found"


def test_update_sport_profile(client):
    # 1. Preparamos los datos que vamos a actualizar en el perfil (ej: id 1)
    payload = {
        "days_per_week": 5,
        "injuries": "Molestia lumbar leve",
    }

    # 2. Hacemos la petición PATCH al endpoint
    response = client.patch("/sport-profiles/1", json=payload)

    # 3. Comprobamos que se actualizó correctamente
    assert response.status_code == 200
    assert response.json()["days_per_week"] == 5
    assert response.json()["injuries"] == "Molestia lumbar leve"


def test_delete_sport_profile(client):
    # 1. Hacemos la petición DELETE a un perfil existente (ej: id 1)
    response = client.delete("/sport-profiles/1")

    # 2. Comprobamos que devuelve 204 No Content
    assert response.status_code == 204
