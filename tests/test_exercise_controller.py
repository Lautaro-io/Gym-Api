from fastapi.testclient import TestClient
# Suponiendo que tu app principal se llama 'app' y está en 'main.py'
from main import app

client = TestClient(app)


def test_create_exercise():
    # 1. Preparamos los datos válidos que vamos a enviar
    payload = {
        "name": "Sentadilla libre",
        "description": "Sentadilla profunda con barra",
        "muscular_group": "pierna",
    }

    # 2. Hacemos la petición POST al endpoint
    response = client.post("/exercises", json=payload)

    # 3. Usamos 'assert' para comprobar que el programa hizo lo esperado
    assert response.status_code == 201
    assert response.json()["name"] == "Sentadilla libre"
    assert response.json()["muscular_group"] == "pierna"


def test_get_exercise():
    # 1. Hacemos la petición GET a un ejercicio existente (ej: id 1)
    response = client.get("/exercises/1")

    # 2. Comprobamos el resultado automáticamente
    assert response.status_code == 200
    assert response.json()["name"] == "Press de banca"
    assert response.json()["muscular_group"] == "pecho"


def test_create_exercise_duplicate_name():
    # 1. Intentamos crear un ejercicio con un nombre que ya existe
    payload = {
        "name": "Press de banca",
        "description": "Intento de ejercicio repetido",
        "muscular_group": "pecho",
    }

    # 2. Hacemos la petición POST al endpoint
    response = client.post("/exercises", json=payload)

    # 3. Comprobamos que el backend rechaza la petición con 409 Conflict
    assert response.status_code == 409
    assert "ya existe" in response.json()["detail"]


def test_create_exercise_invalid_data():
    # 1. Intentamos crear un ejercicio con nombre vacío y grupo muscular inválido
    payload = {
        "name": "",
        "description": "Datos inválidos",
        "muscular_group": "grupo_inexistente",
    }

    # 2. Hacemos la petición POST al endpoint
    response = client.post("/exercises", json=payload)

    # 3. Comprobamos que el backend rechaza la petición por validación (422)
    assert response.status_code == 422


def test_get_exercise_not_found():
    # 1. Hacemos la petición GET a un ejercicio inexistente (ej: id 999)
    response = client.get("/exercises/999")

    # 2. Comprobamos que devuelve 404 Not Found
    assert response.status_code == 404
    assert response.json()["detail"] == "Exercise not found"


def test_update_exercise():
    # 1. Preparamos los campos que queremos actualizar del ejercicio (ej: id 1)
    payload = {
        "description": "Press plano con mancuernas",
    }

    # 2. Hacemos la petición PATCH al endpoint
    response = client.patch("/exercises/1", json=payload)

    # 3. Comprobamos que se actualizó correctamente
    assert response.status_code == 200
    assert response.json()["description"] == "Press plano con mancuernas"


def test_delete_exercise():
    # 1. Hacemos la petición DELETE a un ejercicio existente (ej: id 1)
    response = client.delete("/exercises/1")

    # 2. Comprobamos que devuelve 204 No Content
    assert response.status_code == 204
