from sqlalchemy.orm import Session

from models import SportProfile


class SportProfileRepository:

    def __init__(self, db: Session):
        self.db = db

    def create_new_profile(self, profile_create : SportProfile) -> SportProfile:
        self.db.add(profile_create)
        self.db.commit()
        self.db.refresh(profile_create)
        return profile_create

    def get_all_profiles(self) -> list[SportProfile]:
        return self.db.query(SportProfile).all()

    def get_by_id(self, sport_id: int) -> SportProfile | None  :
        return self.db.query(SportProfile).filter(SportProfile.id == sport_id).first()


    def get_by_user(self, user_id: int) -> list[SportProfile]:
        return self.db.query(SportProfile).filter(SportProfile.user_id == user_id).all()


    def update_profile(self, profile: SportProfile) -> SportProfile:
        self.db.commit()
        self.db.refresh(profile)
        return profile

    def delete_profile(self, profile: SportProfile) -> None:
        self.db.delete(profile)
        self.db.commit()