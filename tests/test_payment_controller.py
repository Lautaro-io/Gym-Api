from datetime import datetime, timedelta, timezone


def _date_from_now(days):
    """Fecha ISO (UTC) a 'days' de hoy. Negativo = en el pasado."""
    return (datetime.now(timezone.utc) + timedelta(days=days)).isoformat()


def _payload(user_id=3, amount="15000.50", method="efectivo", days=30):
    return {
        "user_id": user_id,
        "amount": amount,
        "payment_method": method,
        "expiration_date": _date_from_now(days),
    }


def _create_payment(client, **kwargs):
    """Crea un pago como admin y devuelve el JSON de la respuesta."""
    response = client.post("/payment", json=_payload(**kwargs))
    assert response.status_code == 201
    return response.json()


# ---------- POST /payment ----------

def test_create_payment(client):
    # 1. El admin registra un pago para el cliente (id 3)
    response = client.post("/payment", json=_payload())

    # 2. Comprobamos que se creó con los datos enviados
    assert response.status_code == 201
    assert response.json()["id"] is not None
    assert response.json()["user_id"] == 3
    assert float(response.json()["amount"]) == 15000.50
    assert response.json()["payment_method"] == "efectivo"
    assert response.json()["payment_date"] is not None


def test_create_payment_professor_forbidden(client, auth_profesor):
    # 1. El profesor intenta registrar un pago
    response = client.post("/payment", json=_payload(), headers=auth_profesor)

    # 2. Comprobamos que solo el admin puede (403)
    assert response.status_code == 403


def test_create_payment_customer_forbidden(client, auth_cliente):
    # 1. El cliente intenta registrar un pago
    response = client.post("/payment", json=_payload(), headers=auth_cliente)

    # 2. Comprobamos que devuelve 403
    assert response.status_code == 403


def test_create_payment_invalid_token(client):
    # 1. Enviamos un token inválido
    response = client.post(
        "/payment", json=_payload(), headers={"Authorization": "Bearer token-invalido"}
    )

    # 2. Comprobamos que devuelve 401
    assert response.status_code == 401


def test_create_payment_user_not_found(client):
    # 1. Intentamos registrar un pago para un usuario inexistente (id 999)
    response = client.post("/payment", json=_payload(user_id=999))

    # 2. Comprobamos que devuelve 404
    assert response.status_code == 404
    assert response.json()["detail"] == "User not found"


def test_create_payment_expiration_in_the_past(client):
    # 1. Enviamos una fecha de vencimiento de ayer
    response = client.post("/payment", json=_payload(days=-1))

    # 2. Comprobamos que el servicio lo rechaza (422)
    assert response.status_code == 422
    assert response.json()["detail"] == "expiration_date must be in the future"


def test_create_payment_expiration_without_timezone(client):
    # 1. Enviamos una fecha futura sin zona horaria (el servicio la toma como UTC)
    naive_date = (datetime.now(timezone.utc) + timedelta(days=30)).replace(tzinfo=None).isoformat()
    payload = _payload()
    payload["expiration_date"] = naive_date
    response = client.post("/payment", json=payload)

    # 2. Comprobamos que es válida
    assert response.status_code == 201


def test_create_payment_amount_zero(client):
    # 1. Enviamos un monto en 0 (el schema exige > 0)
    response = client.post("/payment", json=_payload(amount="0"))

    # 2. Comprobamos que devuelve 422
    assert response.status_code == 422


def test_create_payment_amount_negative(client):
    # 1. Enviamos un monto negativo
    response = client.post("/payment", json=_payload(amount="-100"))

    # 2. Comprobamos que devuelve 422
    assert response.status_code == 422


def test_create_payment_invalid_method(client):
    # 1. Enviamos un método de pago que no existe en el enum
    response = client.post("/payment", json=_payload(method="bitcoin"))

    # 2. Comprobamos que devuelve 422
    assert response.status_code == 422


def test_create_payment_invalid_user_id(client):
    # 1. Enviamos user_id en 0 (el schema exige > 0)
    response = client.post("/payment", json=_payload(user_id=0))

    # 2. Comprobamos que devuelve 422
    assert response.status_code == 422


def test_create_payment_missing_fields(client):
    # 1. Enviamos un body incompleto
    response = client.post("/payment", json={"user_id": 3})

    # 2. Comprobamos que devuelve 422
    assert response.status_code == 422


def test_create_payment_all_methods(client):
    # 1. Registramos un pago con cada método válido
    for method in ["tarjeta", "efectivo", "transferencia", "mercado_pago"]:
        response = client.post("/payment", json=_payload(method=method))

        # 2. Comprobamos que todos se aceptan
        assert response.status_code == 201
        assert response.json()["payment_method"] == method


# ---------- GET /payment ----------

def test_get_all_payments(client):
    # 1. Creamos dos pagos
    _create_payment(client)
    _create_payment(client, user_id=2)

    # 2. Listamos como admin
    response = client.get("/payment")

    # 3. Comprobamos que devuelve los dos
    assert response.status_code == 200
    assert len(response.json()) == 2


def test_get_all_payments_empty(client):
    # 1. Listamos sin haber creado pagos
    response = client.get("/payment")

    # 2. Comprobamos que devuelve una lista vacía
    assert response.status_code == 200
    assert response.json() == []


def test_get_all_payments_customer_forbidden(client, auth_cliente):
    # 1. El cliente intenta listar todos los pagos
    response = client.get("/payment", headers=auth_cliente)

    # 2. Comprobamos que devuelve 403
    assert response.status_code == 403


def test_get_all_payments_professor_forbidden(client, auth_profesor):
    # 1. El profesor intenta listar todos los pagos
    response = client.get("/payment", headers=auth_profesor)

    # 2. Comprobamos que devuelve 403
    assert response.status_code == 403


# ---------- GET /payment/{id} ----------

def test_get_payment_by_id(client):
    # 1. Creamos un pago
    payment = _create_payment(client)

    # 2. Lo consultamos por id
    response = client.get(f"/payment/{payment['id']}")

    # 3. Comprobamos que devuelve el mismo pago
    assert response.status_code == 200
    assert response.json()["id"] == payment["id"]
    assert response.json()["user_id"] == 3


def test_get_payment_not_found(client):
    # 1. Consultamos un pago inexistente (id 999)
    response = client.get("/payment/999")

    # 2. Comprobamos que devuelve 404
    assert response.status_code == 404
    assert response.json()["detail"] == "Payment not found"


def test_get_payment_by_id_customer_forbidden(client, auth_cliente):
    # 1. Creamos un pago como admin
    payment = _create_payment(client)

    # 2. El cliente intenta consultarlo por id
    response = client.get(f"/payment/{payment['id']}", headers=auth_cliente)

    # 3. Comprobamos que devuelve 403
    assert response.status_code == 403


# ---------- GET /payment/me ----------

def test_get_my_payments(client, auth_cliente):
    # 1. Creamos dos pagos para el cliente y uno para el profesor
    _create_payment(client, user_id=3)
    _create_payment(client, user_id=3, amount="20000")
    _create_payment(client, user_id=2)

    # 2. El cliente consulta sus pagos
    response = client.get("/payment/me", headers=auth_cliente)

    # 3. Comprobamos que solo ve los suyos
    assert response.status_code == 200
    assert len(response.json()) == 2
    assert all(p["user_id"] == 3 for p in response.json())


def test_get_my_payments_empty(client, auth_cliente):
    # 1. El cliente consulta sin tener pagos
    response = client.get("/payment/me", headers=auth_cliente)

    # 2. Comprobamos que devuelve una lista vacía
    assert response.status_code == 200
    assert response.json() == []


def test_get_my_payments_invalid_token(client):
    # 1. Consultamos con un token inválido
    response = client.get("/payment/me", headers={"Authorization": "Bearer token-invalido"})

    # 2. Comprobamos que devuelve 401
    assert response.status_code == 401


# ---------- GET /payment/me/status ----------

def test_my_status_without_payments(client, auth_cliente):
    # 1. El cliente consulta su membresía sin haber pagado nunca
    response = client.get("/payment/me/status", headers=auth_cliente)

    # 2. Comprobamos que no está vigente
    assert response.status_code == 200
    assert response.json()["vigente"] is False
    assert response.json()["expiration_date"] is None
    assert response.json()["dias_restantes"] == 0


def test_my_status_active(client, auth_cliente):
    # 1. Registramos un pago que vence en 10 días
    _create_payment(client, user_id=3, days=10)

    # 2. El cliente consulta su membresía
    response = client.get("/payment/me/status", headers=auth_cliente)

    # 3. Comprobamos que está vigente (ceil de 9.99.. días = 10)
    assert response.status_code == 200
    assert response.json()["vigente"] is True
    assert response.json()["expiration_date"] is not None
    assert response.json()["dias_restantes"] == 10


def test_my_status_uses_latest_expiration(client, auth_cliente):
    # 1. Registramos un pago a 5 días y otro a 30 días (en ese orden)
    _create_payment(client, user_id=3, days=5)
    _create_payment(client, user_id=3, days=30)

    # 2. Consultamos la membresía
    response = client.get("/payment/me/status", headers=auth_cliente)

    # 3. Comprobamos que toma el vencimiento más lejano
    assert response.status_code == 200
    assert response.json()["dias_restantes"] == 30


def test_my_status_expired(client, auth_cliente):
    # 1. Insertamos directo en la base un pago ya vencido, porque el endpoint
    #    POST no permite crear pagos con vencimiento en el pasado
    from conftest import TestingSessionLocal
    from models import Payment
    from models.enums import MetodoPagoEnum

    session = TestingSessionLocal()
    try:
        session.add(
            Payment(
                user_id=3,
                amount=5000,
                payment_method=MetodoPagoEnum.EFECTIVO,
                expiration_date=datetime.now(timezone.utc) - timedelta(days=3),
            )
        )
        session.commit()
    finally:
        session.close()

    # 2. El cliente consulta su membresía
    response = client.get("/payment/me/status", headers=auth_cliente)

    # 3. Comprobamos que figura vencida y con 0 días restantes
    assert response.status_code == 200
    assert response.json()["vigente"] is False
    assert response.json()["expiration_date"] is not None
    assert response.json()["dias_restantes"] == 0


# ---------- GET /payment/{id}/status ----------

def test_user_status_admin(client):
    # 1. Registramos un pago a 15 días para el cliente
    _create_payment(client, user_id=3, days=15)

    # 2. El admin consulta la membresía del cliente
    response = client.get("/payment/3/status")

    # 3. Comprobamos que está vigente
    assert response.status_code == 200
    assert response.json()["vigente"] is True
    assert response.json()["dias_restantes"] == 15


def test_user_status_without_payments(client):
    # 1. El admin consulta la membresía de un usuario sin pagos
    response = client.get("/payment/3/status")

    # 2. Comprobamos que no está vigente
    assert response.status_code == 200
    assert response.json()["vigente"] is False
    assert response.json()["dias_restantes"] == 0


def test_user_status_not_found(client):
    # 1. El admin consulta la membresía de un usuario inexistente (id 999)
    response = client.get("/payment/999/status")

    # 2. Comprobamos que devuelve 404
    assert response.status_code == 404
    assert response.json()["detail"] == "User not found"


def test_user_status_customer_forbidden(client, auth_cliente):
    # 1. El cliente intenta consultar la membresía de otro usuario
    response = client.get("/payment/2/status", headers=auth_cliente)

    # 2. Comprobamos que devuelve 403
    assert response.status_code == 403