def test_get_users_admin(client):
    # 1. Listamos los usuarios con token de admin
    response = client.get("/users")

    # 2. Comprobamos que devuelve los 3 usuarios sembrados
    assert response.status_code == 200
    assert len(response.json()) == 3


def test_get_users_profesor(client, auth_profesor):
    # 1. Listamos los usuarios con token de profesor
    response = client.get("/users", headers=auth_profesor)

    # 2. Comprobamos que el profesor también puede leer
    assert response.status_code == 200
    assert len(response.json()) == 3


def test_get_users_cliente_forbidden(client, auth_cliente):
    # 1. Intentamos listar usuarios con token de cliente
    response = client.get("/users", headers=auth_cliente)

    # 2. Comprobamos que el backend lo rechaza por permisos (403)
    assert response.status_code == 403


def test_get_user_by_id(client):
    # 1. Pedimos el usuario cliente (id 3)
    response = client.get("/users/3")

    # 2. Comprobamos que devuelve sus datos
    assert response.status_code == 200
    assert response.json()["email"] == "cliente@gymsass.com"


def test_get_user_not_found(client):
    # 1. Pedimos un usuario inexistente (id 999)
    response = client.get("/users/999")

    # 2. Comprobamos que devuelve 404
    assert response.status_code == 404
    assert response.json()["detail"] == "User not found"


def test_get_me(client, auth_cliente):
    # 1. El cliente pide sus propios datos
    response = client.get("/users/me", headers=auth_cliente)

    # 2. Comprobamos que devuelve el usuario del token
    assert response.status_code == 200
    assert response.json()["id"] == 3
    assert response.json()["email"] == "cliente@gymsass.com"


def test_update_me(client, auth_cliente):
    # 1. El cliente actualiza su propio nombre y teléfono
    payload = {"name": "Juan Carlos", "phone": "1199999999"}
    response = client.patch("/users/me", json=payload, headers=auth_cliente)

    # 2. Comprobamos que se actualizó
    assert response.status_code == 200
    assert response.json()["name"] == "Juan Carlos"
    assert response.json()["phone"] == "1199999999"


def test_update_me_no_puede_cambiar_rol(client, auth_cliente):
    # 1. El cliente intenta cambiarse el rol por el PATCH de sus datos
    response = client.patch("/users/me", json={"rol": "admin"}, headers=auth_cliente)

    # 2. Comprobamos que el campo se ignora y sigue siendo cliente
    assert response.status_code == 200
    assert response.json()["rol"] == "cliente"


def test_update_user_admin(client):
    # 1. El admin actualiza parcialmente al cliente (id 3)
    response = client.patch("/users/3", json={"lastname": "Perez Gomez"})

    # 2. Comprobamos que se actualizó
    assert response.status_code == 200
    assert response.json()["lastname"] == "Perez Gomez"


def test_update_user_profesor_forbidden(client, auth_profesor):
    # 1. El profesor intenta editar a un usuario
    response = client.patch("/users/3", json={"name": "Otro"}, headers=auth_profesor)

    # 2. Comprobamos que solo el admin puede escribir (403)
    assert response.status_code == 403


def test_update_user_duplicate_email(client):
    # 1. Intentamos ponerle al cliente el email del admin
    response = client.patch("/users/3", json={"email": "admin@gymsass.com"})

    # 2. Comprobamos que rechaza el duplicado (409)
    assert response.status_code == 409
    assert "email" in response.json()["detail"]


def test_update_user_null_field(client):
    # 1. Intentamos dejar el nombre en null
    response = client.patch("/users/3", json={"name": None})

    # 2. Comprobamos que el backend lo rechaza (400)
    assert response.status_code == 400
    assert response.json()["detail"] == "El campo name no puede ser null"


def test_update_user_dni_invalido(client):
    # 1. Intentamos poner un dni de 9 caracteres (máximo permitido: 8)
    response = client.patch("/users/3", json={"dni": "123456789"})

    # 2. Comprobamos que el backend lo rechaza por validación (422)
    assert response.status_code == 422


def test_update_rol(client):
    # 1. El admin le asigna el rol de profesor al cliente (id 3)
    response = client.patch("/users/3/rol", json={"rol": "profesor"})

    # 2. Comprobamos que el rol cambió
    assert response.status_code == 200
    assert response.json()["rol"] == "profesor"


def test_update_rol_propio(client):
    # 1. El admin intenta cambiarse su propio rol (id 1)
    response = client.patch("/users/1/rol", json={"rol": "cliente"})

    # 2. Comprobamos que el backend lo rechaza (400)
    assert response.status_code == 400
    assert response.json()["detail"] == "No puedes cambiar tu propio rol"


def test_delete_user_baja_logica_y_reactivar(client):
    # 1. Damos de baja al cliente (id 3)
    response = client.delete("/users/3")

    # 2. Comprobamos que devuelve 204 y que la fila sigue existiendo como INACTIVO
    assert response.status_code == 204

    baja = client.get("/users/3")
    assert baja.status_code == 200
    assert baja.json()["state"] == "inactivo"

    # 3. Lo reactivamos con el endpoint de habilitar
    reactivado = client.patch("/users/3/habilitar")
    assert reactivado.status_code == 200
    assert reactivado.json()["state"] == "habilitado_entrenar"


def test_delete_user_cliente_forbidden(client, auth_cliente):
    # 1. El cliente intenta darse de baja
    response = client.delete("/users/3", headers=auth_cliente)

    # 2. Comprobamos que solo el admin puede borrar (403)
    assert response.status_code == 403


def test_delete_user_not_found(client):
    # 1. Intentamos dar de baja un usuario inexistente (id 999)
    response = client.delete("/users/999")

    # 2. Comprobamos que devuelve 404
    assert response.status_code == 404
