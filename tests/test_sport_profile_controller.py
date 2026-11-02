"""
Pruebas de integración del módulo SportProfile (/sport-profiles) usando FastAPI TestClient.
ISFT N.° 194 - Metodología de Pruebas de Sistemas.
"""


def test_create_sport_profile_success(client, auth_headers_admin):
    """CP-SP-01: Alta exitosa de perfil deportivo (201 Created)."""
    payload = {
        "user_id": 3,
        "goal": "Definición muscular",
        "level": "Avanzado",
        "days_per_week": 5,
        "session_duration": 75,
        "age": 28,
        "injuries": None,
        "trainer_tracking": True,
    }
    response = client.post("/sport-profiles", json=payload, headers=auth_headers_admin)
    assert response.status_code == 201
    data = response.json()
    assert data["user_id"] == 3
    assert data["goal"] == "Definición muscular"
    assert data["days_per_week"] == 5


def test_get_sport_profile_by_id_success(client, auth_headers_admin):
    """CP-SP-02: GET exitoso de un perfil deportivo por ID (200 OK)."""
    # 1. Hacemos la petición GET a un perfil existente (ID 1)
    response = client.get("/sport-profiles/1", headers=auth_headers_admin)
    # 2. Comprobamos el resultado automáticamente
    assert response.status_code == 200
    assert response.json()["goal"] == "Hipertrofia muscular"
    assert response.json()["days_per_week"] == 4


def test_get_my_sport_profiles_success(client, auth_headers_cliente):
    """CP-SP-03: GET /sport-profiles/me devuelve los perfiles del usuario autenticado."""
    response = client.get("/sport-profiles/me", headers=auth_headers_cliente)
    assert response.status_code == 200
    perfiles = response.json()
    assert len(perfiles) == 1
    assert perfiles[0]["user_id"] == 3


def test_create_sport_profile_invalid_ranges(client, auth_headers_admin):
    """CP-SP-04: POST fallido por días por semana (> 7) y edad inválida (<= 10) (422)."""
    # 1. Intentamos crear un perfil con valores fuera de rango
    payload = {
        "user_id": 3,
        "goal": "Bajar de peso",
        "level": "Principiante",
        "days_per_week": 9,
        "session_duration": -30,
        "age": 5,
        "injuries": None,
        "trainer_tracking": False,
    }
    response = client.post("/sport-profiles", json=payload, headers=auth_headers_admin)
    # 2. Comprobamos que el backend rechaza la petición
    assert response.status_code == 422


def test_create_sport_profile_user_not_found(client, auth_headers_admin):
    """CP-SP-05: POST fallido cuando el user_id no existe (404 Not Found)."""
    payload = {
        "user_id": 9999,
        "goal": "Fuerza máxima",
        "level": "Avanzado",
        "days_per_week": 4,
        "session_duration": 60,
        "age": 30,
        "injuries": None,
        "trainer_tracking": False,
    }
    response = client.post("/sport-profiles", json=payload, headers=auth_headers_admin)
    assert response.status_code == 404
    assert response.json()["detail"] == "User not found"


def test_get_sport_profile_not_found(client, auth_headers_admin):
    """CP-SP-06: GET a un perfil deportivo inexistente (404 Not Found)."""
    response = client.get("/sport-profiles/999", headers=auth_headers_admin)
    assert response.status_code == 404
    assert response.json()["detail"] == "Sport profile not found"


def test_update_sport_profile_partial_success(client, auth_headers_admin):
    """CP-SP-07: Actualización parcial exitosa de perfil deportivo (200 OK)."""
    payload = {"days_per_week": 5, "injuries": "Molestia lumbar leve"}
    response = client.patch("/sport-profiles/1", json=payload, headers=auth_headers_admin)
    assert response.status_code == 200
    data = response.json()
    assert data["days_per_week"] == 5
    assert data["injuries"] == "Molestia lumbar leve"


def test_get_all_sport_profiles_forbidden_for_non_admin(client, auth_headers_cliente):
    """CP-SP-08: Un usuario que no es Admin no puede listar todos los perfiles (403)."""
    response = client.get("/sport-profiles", headers=auth_headers_cliente)
    assert response.status_code == 403
    assert "Solo Administradores" in response.json()["detail"]


def test_delete_sport_profile_success(client, auth_headers_admin):
    """CP-SP-09: Eliminación exitosa de perfil deportivo por Admin (204 No Content)."""
    response = client.delete("/sport-profiles/1", headers=auth_headers_admin)
    assert response.status_code == 204

    get_res = client.get("/sport-profiles/1", headers=auth_headers_admin)
    assert get_res.status_code == 404
