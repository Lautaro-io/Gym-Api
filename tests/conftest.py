import os

# Configurar variables de entorno de prueba antes de importar la app.
# Asignacion directa (no setdefault): si el shell ya tiene DATABASE_URL
# apuntando a SQL Server, drop_all borraria la base real.
os.environ["DATABASE_URL"] = "sqlite://"
os.environ["SECRET_KEY"] = "clave-secreta-de-prueba-isft-194-testing-2026"
os.environ["ALGORITHM"] = "HS256"

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

import db as db_module
from models import Exercise, SportProfile, User
from models.enums import GrupoMuscularEnum, RolEnum, UserStateEnum

# Engine SQLite en memoria compartido para TestClient
TEST_ENGINE = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=TEST_ENGINE)

# Se pisan antes de importar main, que ejecuta init_db() al importarse
db_module.engine = TEST_ENGINE
db_module.SessionLocal = TestingSessionLocal

from main import app
from security.jwt_service import create_access_token

ADMIN_ID = 1
PROFESOR_ID = 2
CLIENTE_ID = 3


def override_get_db():
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


app.dependency_overrides[db_module.get_db] = override_get_db


def _auth_headers(user_id: int) -> dict[str, str]:
    token = create_access_token({"sub": str(user_id)})
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture(autouse=True)
def setup_database():
    """Reinicia las tablas antes de cada test y carga datos iniciales."""
    db_module.Base.metadata.drop_all(bind=TEST_ENGINE)
    db_module.Base.metadata.create_all(bind=TEST_ENGINE)

    session = TestingSessionLocal()
    try:
        admin = User(
            id=ADMIN_ID,
            dni="11111111",
            name="Admin",
            lastname="Sistema",
            phone="1100000001",
            email="admin@gymsass.com",
            hashed_password="hashed_password",
            rol=RolEnum.ADMIN,
            state=UserStateEnum.HABILITADO_ENTRENAR,
        )
        profesor = User(
            id=PROFESOR_ID,
            dni="22222222",
            name="Profe",
            lastname="Entrenador",
            phone="1100000002",
            email="profe@gymsass.com",
            hashed_password="hashed_password",
            rol=RolEnum.PROFESOR,
            state=UserStateEnum.ACTIVO,
        )
        cliente = User(
            id=CLIENTE_ID,
            dni="33333333",
            name="Juan",
            lastname="Perez",
            phone="1100000003",
            email="cliente@gymsass.com",
            hashed_password="hashed_password",
            rol=RolEnum.CLIENTE,
            state=UserStateEnum.HABILITADO_ENTRENAR,
        )
        ejercicio_inicial = Exercise(
            id=1,
            name="Press de banca",
            description="Press plano con barra olímpica",
            muscular_group=GrupoMuscularEnum.PECHO,
        )
        perfil_inicial = SportProfile(
            id=1,
            user_id=ADMIN_ID,
            goal="Hipertrofia muscular",
            level="Intermedio",
            days_per_week=4,
            session_duration=60,
            age=25,
            injuries="Ninguna",
            trainer_tracking=True,
        )
        session.add_all([admin, profesor, cliente, ejercicio_inicial, perfil_inicial])
        session.commit()
        yield
    finally:
        session.close()


@pytest.fixture
def client():
    """TestClient con token de ADMIN por defecto.

    Para probar otro rol o la falta de token, pasar headers explicitos:
    client.get("/users", headers=auth_cliente) / headers={"Authorization": "Bearer malo"}
    """
    with TestClient(app, headers=_auth_headers(ADMIN_ID)) as test_client:
        yield test_client


@pytest.fixture
def auth_admin():
    return _auth_headers(ADMIN_ID)


@pytest.fixture
def auth_profesor():
    return _auth_headers(PROFESOR_ID)


@pytest.fixture
def auth_cliente():
    return _auth_headers(CLIENTE_ID)
