from models import User
from repositories.user_repository import UserRepository
from schemas.user_schema import UserCreate


class UserService:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    def get_user(self, user_id: int) -> User | None:
        return self.user_repository.get_by_id(user_id)

    def get_all_users(self) -> list[User]:
        return self.user_repository.get_all()

    def create_user(self, user: User) -> User:
        return self.user_repository.create(user)

    def update_user(self, user: User) -> User:
        return self.user_repository.update(user)

    def delete_user(self, user: User) -> None:
        self.user_repository.delete(user)