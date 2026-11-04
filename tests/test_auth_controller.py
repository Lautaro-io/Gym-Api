REGISTRO = {
    "email": "nuevo@gymsass.com",
    "password": "Password123",
    "name": "Nuevo",
    "lastname": "Usuario",
    "dni": "44444444",
    "phone": "1100000004",
}


def test_register_user(client):
    #  Hacemos la petición POST al endpoint de registro
    response = client.post("/auth/register", json=REGISTRO)

    # Comprobamos que se creó con los valores por defecto y sin contraseña
    assert response.status_code == 201
    assert response.json()["email"] == REGISTRO["email"]
    assert response.json()["rol"] == "cliente"
    assert response.json()["state"] == "pendiente_habilitacion"
    assert "password" not in response.json()
    assert "hashed_password" not in response.json()


def test_register_duplicate_email(client):
    # 1. Registramos un usuario
    client.post("/auth/register", json=REGISTRO)

    # 2. Intentamos registrarlo otra vez
    response = client.post("/auth/register", json=REGISTRO)

    # 3. Comprobamos que el backend rechaza el email repetido con 409
    assert response.status_code == 409
    assert "email" in response.json()["detail"]


def test_register_invalid_data(client):
    # 1. Preparamos datos inválidos (password corta y email inválido)
    payload = {
        "email": "no-es-un-email",
        "password": "1234567",
        "name": "Nuevo",
        "lastname": "Usuario",
        "dni": "44444444",
        "phone": "1100000004",
    }

    # 2. Hacemos la petición POST al endpoint
    response = client.post("/auth/register", json=payload)

    # 3. Comprobamos que el backend rechaza los datos por validación (422)
    assert response.status_code == 422


def test_register_limite_valido(client):
    # 1. Preparamos datos en el límite (password de 8 y dni de 7)
    payload = {
        "email": "limite@gymsass.com",
        "password": "12345678",
        "name": "Nuevo",
        "lastname": "Usuario",
        "dni": "1234567",
        "phone": "1100000005",
    }

    # 2. Hacemos la petición al endpoint
    response = client.post("/auth/register", json=payload)

    # 3. Comprobamos que el límite mínimo es aceptado
    assert response.status_code == 201


def test_register_dni_invalido(client):
    # 1. Preparamos un dni de 9 caracteres (máximo permitido: 8)
    payload = dict(REGISTRO, dni="123456789")

    # 2. Hacemos la petición POST al endpoint
    response = client.post("/auth/register", json=payload)

    # 3. Comprobamos que el backend lo rechaza por validación (422)
    assert response.status_code == 422


def test_login_ok(client):
    # 1. Registramos el usuario
    client.post("/auth/register", json=REGISTRO)

    # 2. Hacemos login con form data (el endpoint es OAuth2, no JSON)
    response = client.post(
        "/auth/login",
        data={"username": REGISTRO["email"], "password": REGISTRO["password"]},
    )

    # 3. Comprobamos que devuelve un token
    assert response.status_code == 200
    assert response.json()["token_type"] == "bearer"
    token = response.json()["access_token"]

    me = client.get("/users/me", headers={"Authorization": f"Bearer {token}"})
    assert me.status_code == 200
    assert me.json()["email"] == REGISTRO["email"]


def test_login_wrong_password(client):
    # 1. Registramos el usuario
    client.post("/auth/register", json=REGISTRO)

    # 2. Intentamos loguearnos con una contraseña incorrecta
    response = client.post(
        "/auth/login",
        data={"username": REGISTRO["email"], "password": "PasswordIncorrecta"},
    )

    # 3. Comprobamos que devuelve 401
    assert response.status_code == 401
    assert response.json()["detail"] == "Contraseña incorrecta"


def test_login_user_not_found(client):
    # 1. Intentamos loguearnos con un email que no existe
    response = client.post(
        "/auth/login",
        data={"username": "noexiste@gymsass.com", "password": "Password123"},
    )

    # 2. Comprobamos el comportamiento actual del backend: 404
    assert response.status_code == 404
    assert response.json()["detail"] == "Usuario no encontrado"


def test_protected_route_invalid_token(client):
    # 1. Hacemos una petición con un token inválido
    response = client.get("/users/me", headers={"Authorization": "Bearer token-invalido"})

    # 2. Comprobamos que devuelve 401
    assert response.status_code == 401
    assert response.json()["detail"] == "Token inválido"


def test_update_password_ok(client):
    # 1. Registramos el usuario y nos logueamos
    client.post("/auth/register", json=REGISTRO)
    login = client.post(
        "/auth/login",
        data={"username": REGISTRO["email"], "password": REGISTRO["password"]},
    )
    token = login.json()["access_token"]

    # 2. Cambiamos la contraseña
    response = client.patch(
        "/auth/password",
        json={"old_password": REGISTRO["password"], "new_password": "PasswordNueva123"},
        headers={"Authorization": f"Bearer {token}"},
    )

    # 3. Comprobamos que la nueva contraseña funciona y la vieja ya no
    assert response.status_code == 200

    nuevo_login = client.post(
        "/auth/login",
        data={"username": REGISTRO["email"], "password": "PasswordNueva123"},
    )
    assert nuevo_login.status_code == 200

    viejo_login = client.post(
        "/auth/login",
        data={"username": REGISTRO["email"], "password": REGISTRO["password"]},
    )
    assert viejo_login.status_code == 401


def test_update_password_wrong_old(client):
    # 1. Registramos el usuario y nos logueamos
    client.post("/auth/register", json=REGISTRO)
    login = client.post(
        "/auth/login",
        data={"username": REGISTRO["email"], "password": REGISTRO["password"]},
    )
    token = login.json()["access_token"]

    # 2. Intentamos cambiar la contraseña con una vieja incorrecta
    response = client.patch(
        "/auth/password",
        json={"old_password": "PasswordIncorrecta", "new_password": "PasswordNueva123"},
        headers={"Authorization": f"Bearer {token}"},
    )

    # 3. Comprobamos que devuelve 400
    assert response.status_code == 400
    assert response.json()["detail"] == "Contraseña incorrecta"
