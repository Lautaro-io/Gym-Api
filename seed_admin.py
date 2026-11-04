"""Crea el primer administrador de forma idempotente.

Uso (desde la raíz del proyecto):

    .\\.venv\\Scripts\\python.exe seed_admin.py

Los datos se pueden personalizar con variables de entorno (ADMIN_EMAIL,
ADMIN_PASSWORD, ADMIN_NAME, ADMIN_LASTNAME, ADMIN_DNI, ADMIN_PHONE).
Si ya existe un usuario con ese email, DNI o teléfono, no crea nada.
"""

import os

from db import SessionLocal, init_db
from models import User
from models.enums import RolEnum, UserStateEnum
from repositories.user_repository import UserRepository
from services.password_service import hash_password

ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "admin@gymsass.com")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "Admin1234!")
ADMIN_NAME = os.getenv("ADMIN_NAME", "Admin")
ADMIN_LASTNAME = os.getenv("ADMIN_LASTNAME", "Sistema")
ADMIN_DNI = os.getenv("ADMIN_DNI", "10000000")
ADMIN_PHONE = os.getenv("ADMIN_PHONE", "1100000000")


def main() -> None:
    init_db()
    db = SessionLocal()
    try:
        repository = UserRepository(db)
        existing = (
            repository.get_by_email(ADMIN_EMAIL)
            or repository.get_by_dni(ADMIN_DNI)
            or repository.get_by_phone(ADMIN_PHONE)
        )
        if existing:
            print(f"Ya existe un usuario con ese email, DNI o teléfono: {existing.email} (sin cambios)")
            return

        admin = User(
            dni=ADMIN_DNI,
            name=ADMIN_NAME,
            lastname=ADMIN_LASTNAME,
            phone=ADMIN_PHONE,
            email=ADMIN_EMAIL,
            hashed_password=hash_password(ADMIN_PASSWORD),
            rol=RolEnum.ADMIN,
            state=UserStateEnum.HABILITADO_ENTRENAR,
        )
        repository.create(admin)
        print(f"Admin creado: {ADMIN_EMAIL}")
        print(f"Contraseña inicial: {ADMIN_PASSWORD} (cambiala con PATCH /auth/password)")
    finally:
        db.close()


if __name__ == "__main__":
    main()
