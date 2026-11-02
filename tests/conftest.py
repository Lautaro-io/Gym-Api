import os

# Configurar variables de entorno de prueba antes de importar la app
os.environ.setdefault("DATABASE_URL", "sqlite://")
os.environ.setdefault("SECRET_KEY", "clave-secreta-de-prueba-isft-194-testing-2026")
os.environ.setdefault("ALGORITHM", "HS256")

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

import db as db_module
from models import Exercise, SportProfile, User
from models.enums import GrupoMuscularEnum, RolEnum, UserStateEnum
from security.jwt_service import get_current_user

# Engine SQLite en memoria compartido para TestClient
TEST_ENGINE = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=TEST_ENGINE)

db_module.engine = TEST_ENGINE
db_module.SessionLocal = TestingSessionLocal

from main import app  # noqa: E402


def override_get_db():
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


def override_get_current_user():
    session = TestingSessionLocal()
    try:
        return session.query(User).filter(User.id == 1).first()
    finally:
        session.close()


app.dependency_overrides[db_module.get_db] = override_get_db
app.dependency_overrides[get_current_user] = override_get_current_user


@pytest.fixture(autouse=True)
def setup_database():
    """Reinicia las tablas antes de cada test y carga datos iniciales."""
    db_module.Base.metadata.drop_all(bind=TEST_ENGINE)
    db_module.Base.metadata.create_all(bind=TEST_ENGINE)

    session = TestingSessionLocal()
    try:
        usuario_inicial = User(
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
        ejercicio_inicial = Exercise(
            id=1,
            name="Press de banca",
            description="Press plano con barra olímpica",
            muscular_group=GrupoMuscularEnum.PECHO,
        )
        perfil_inicial = SportProfile(
            id=1,
            user_id=1,
            goal="Hipertrofia muscular",
            level="Intermedio",
            days_per_week=4,
            session_duration=60,
            age=25,
            injuries="Ninguna",
            trainer_tracking=True,
        )
        session.add_all([usuario_inicial, ejercicio_inicial, perfil_inicial])
        session.commit()
        yield
    finally:
        session.close()
