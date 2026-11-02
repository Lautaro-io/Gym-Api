import os

# Configurar variables de entorno de prueba antes de importar la app
os.environ.setdefault("DATABASE_URL", "sqlite://")
os.environ.setdefault("SECRET_KEY", "clave-secreta-de-prueba-isft-194-testing-2026")
os.environ.setdefault("ALGORITHM", "HS256")

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

import db as db_module
from models import Exercise, SportProfile, User
from models.enums import GrupoMuscularEnum, RolEnum, UserStateEnum
from security.jwt_service import create_access_token

# Engine SQLite en memoria compartido entre hilos para TestClient
TEST_ENGINE = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=TEST_ENGINE)

# Reemplazamos el engine de db antes de importar main (que ejecuta init_db())
db_module.engine = TEST_ENGINE
db_module.SessionLocal = TestingSessionLocal

from main import app  # noqa: E402


@pytest.fixture()
def db_session():
    """Reinicia las tablas en cada test y carga datos semilla básicos."""
    db_module.Base.metadata.drop_all(bind=TEST_ENGINE)
    db_module.Base.metadata.create_all(bind=TEST_ENGINE)

    session = TestingSessionLocal()
    try:
        admin_user = User(
            id=1,
            dni="11111111",
            name="Admin",
            lastname="Sistema",
            phone="1100000001",
            email="admin@gymsass.com",
            hashed_password="hashed_password",
            rol=RolEnum.ADMIN,
            state=UserStateEnum.ACTIVO,
        )
        profesor_user = User(
            id=2,
            dni="22222222",
            name="Profe",
            lastname="Entrenador",
            phone="1100000002",
            email="profe@gymsass.com",
            hashed_password="hashed_password",
            rol=RolEnum.PROFESOR,
            state=UserStateEnum.ACTIVO,
        )
        cliente_user = User(
            id=3,
            dni="33333333",
            name="Juan",
            lastname="Perez",
            phone="1100000003",
            email="cliente@gymsass.com",
            hashed_password="hashed_password",
            rol=RolEnum.CLIENTE,
            state=UserStateEnum.HABILITADO_ENTRENAR,
        )
        session.add_all([admin_user, profesor_user, cliente_user])

        ejercicio_inicial = Exercise(
            id=1,
            name="Press de banca",
            description="Press plano con barra olímpica",
            muscular_group=GrupoMuscularEnum.PECHO,
        )
        session.add(ejercicio_inicial)

        perfil_inicial = SportProfile(
            id=1,
            user_id=3,
            goal="Hipertrofia muscular",
            level="Intermedio",
            days_per_week=4,
            session_duration=60,
            age=25,
            injuries="Ninguna",
            trainer_tracking=True,
        )
        session.add(perfil_inicial)
        session.commit()

        yield session
    finally:
        session.close()


@pytest.fixture()
def client(db_session):
    """Cliente de pruebas de FastAPI conectado a la sesión SQLite en memoria."""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[db_module.get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture()
def auth_headers_admin():
    token = create_access_token({"sub": "1"})
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture()
def auth_headers_profesor():
    token = create_access_token({"sub": "2"})
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture()
def auth_headers_cliente():
    token = create_access_token({"sub": "3"})
    return {"Authorization": f"Bearer {token}"}
