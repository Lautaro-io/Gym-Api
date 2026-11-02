"""
Pruebas de integración del módulo Exercise (/exercises) usando FastAPI TestClient.
ISFT N.° 194 - Metodología de Pruebas de Sistemas.
"""


def test_create_exercise_success(client, auth_headers_profesor):
    """CP-EX-01: Alta exitosa de un ejercicio nuevo (201 Created)."""
    payload = {
        "name": "Sentadilla libre",
        "description": "Sentadilla profunda con barra",
        "muscular_group": "pierna",
    }
    response = client.post("/exercises", json=payload, headers=auth_headers_profesor)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Sentadilla libre"
    assert data["muscular_group"] == "pierna"
    assert "id" in data


def test_get_exercise_by_id_success(client, auth_headers_cliente):
    """CP-EX-02: GET exitoso de un ejercicio existente (ID 1)."""
    # 1. Hacemos la petición GET a un ejercicio existente (ID 1)
    response = client.get("/exercises/1", headers=auth_headers_cliente)
    # 2. Comprobamos el resultado automáticamente
    assert response.status_code == 200
    assert response.json()["name"] == "Press de banca"
    assert response.json()["muscular_group"] == "pecho"


def test_get_exercises_filtered_by_muscular_group(client, auth_headers_cliente):
    """CP-EX-03: Listado filtrado por grupo muscular."""
    response = client.get("/exercises?muscular_group=pecho", headers=auth_headers_cliente)
    assert response.status_code == 200
    items = response.json()
    assert len(items) == 1
    assert items[0]["muscular_group"] == "pecho"


def test_create_exercise_duplicate_name(client, auth_headers_profesor):
    """CP-EX-04: POST fallido por nombre de ejercicio duplicado (409 Conflict)."""
    payload = {
        "name": "Press de banca",
        "description": "Intento de duplicado",
        "muscular_group": "pecho",
    }
    response = client.post("/exercises", json=payload, headers=auth_headers_profesor)
    assert response.status_code == 409
    assert "ya existe" in response.json()["detail"]


def test_create_exercise_invalid_muscular_group(client, auth_headers_profesor):
    """CP-EX-05: POST fallido por grupo muscular inválido y nombre vacío (422)."""
    payload = {
        "name": "",
        "description": "Grupo muscular inexistente",
        "muscular_group": "antebrazo_invalido",
    }
    response = client.post("/exercises", json=payload, headers=auth_headers_profesor)
    assert response.status_code == 422


def test_get_exercise_not_found(client, auth_headers_cliente):
    """CP-EX-06: GET a un ejercicio inexistente devuelve 404 Not Found."""
    response = client.get("/exercises/999", headers=auth_headers_cliente)
    assert response.status_code == 404
    assert response.json()["detail"] == "Exercise not found"


def test_update_exercise_partial_success(client, auth_headers_profesor):
    """CP-EX-07: Actualización parcial exitosa mediante PATCH (200 OK)."""
    payload = {"description": "Press plano con mancuernas"}
    response = client.patch("/exercises/1", json=payload, headers=auth_headers_profesor)
    assert response.status_code == 200
    assert response.json()["description"] == "Press plano con mancuernas"
    assert response.json()["name"] == "Press de banca"


def test_delete_exercise_forbidden_for_cliente(client, auth_headers_cliente):
    """CP-EX-08: Cliente sin permisos intenta eliminar un ejercicio (403 Forbidden)."""
    response = client.delete("/exercises/1", headers=auth_headers_cliente)
    assert response.status_code == 403
    assert "Se requiere rol de Profesor" in response.json()["detail"]


def test_delete_exercise_success(client, auth_headers_profesor):
    """CP-EX-09: Eliminación exitosa de un ejercicio por Profesor (204 No Content)."""
    response = client.delete("/exercises/1", headers=auth_headers_profesor)
    assert response.status_code == 204

    # Verificamos que ya no existe
    get_res = client.get("/exercises/1", headers=auth_headers_profesor)
    assert get_res.status_code == 404
