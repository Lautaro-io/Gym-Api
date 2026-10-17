from fastapi import HTTPException

from models import SportProfile
from repositories.sport_profile_repository import SportProfileRepository
from repositories.user_repository import UserRepository
from schemas.sport_profile_schema import SportProfileCreate, SportProfileUpdate


class SportProfileService:
    def __init__(self, sport_profile_repository: SportProfileRepository, user_repository: UserRepository):
        self.sport_profile_repository = sport_profile_repository
        self.user_repository = user_repository

    def get_sport_profile(self, sport_id: int) -> SportProfile | None:
        sport_profile =  self.sport_profile_repository.get_by_id(sport_id)
        if not sport_profile:
            raise HTTPException(status_code=404, detail="Sport profile not found")
        return sport_profile


    def get_sport_profiles_by_user(self, user_id: int) -> list[SportProfile]:
        user = self.user_repository.get_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return self.sport_profile_repository.get_by_user(user_id)

    def get_all_sport_profiles(self) -> list[SportProfile]:
        return self.sport_profile_repository.get_all_profiles()

    def create_sport_profile(self, user_id: int, sport_data: SportProfileCreate) -> SportProfile:
        user = self.user_repository.get_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        sport_profile = SportProfile(**sport_data.model_dump())
        return self.sport_profile_repository.create_new_profile(sport_profile)

    def update_sport_profile(self, sport_id: int, sport_data: SportProfileUpdate) -> SportProfile:
        sport_profile = self.sport_profile_repository.get_by_id(sport_id)
        if not sport_profile:
            raise HTTPException(status_code=404, detail="Sport profile not found")
        for campo, valor in sport_data.model_dump(exclude_unset=True).items():
            setattr(sport_profile, campo, valor)
        return self.sport_profile_repository.update_profile(sport_profile)

    def delete_sport_profile(self, sport_id: int) -> None:
        sport_profile = self.sport_profile_repository.get_by_id(sport_id)
        if not sport_profile:
            raise HTTPException(status_code=404, detail="Sport profile not found")
        self.sport_profile_repository.delete_profile(sport_profile)
