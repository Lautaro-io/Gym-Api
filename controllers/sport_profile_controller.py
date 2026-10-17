from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from starlette import status

from db import get_db
from models import User
from repositories.sport_profile_repository import SportProfileRepository
from repositories.user_repository import UserRepository
from schemas.sport_profile_schema import SportProfileCreate, SportProfileResponse, SportProfileUpdate
from security.jwt_service import get_current_user
from security.permissions import require_admin
from services.sport_profile_service import SportProfileService

router = APIRouter(prefix="/sport-profiles", tags=["Sport Profiles"])


@router.post("", response_model=SportProfileResponse, status_code=status.HTTP_201_CREATED)
def create_sport_profile(sport_data: SportProfileCreate, current_user: User = Depends(require_admin),
                         db: Session = Depends(get_db)) -> SportProfileResponse:
    sport_service = SportProfileService(SportProfileRepository(db), UserRepository(db))
    return sport_service.create_sport_profile(sport_data.user_id, sport_data)


@router.get("", response_model=list[SportProfileResponse])
def get_sport_profiles(current_user: User = Depends(require_admin),
                       db: Session = Depends(get_db)) -> list[SportProfileResponse]:
    sport_service = SportProfileService(SportProfileRepository(db), UserRepository(db))
    return sport_service.get_all_sport_profiles()


@router.get("/me", response_model=list[SportProfileResponse])
def get_my_sport_profiles(current_user: User = Depends(get_current_user),
                          db: Session = Depends(get_db)) -> list[SportProfileResponse]:
    sport_service = SportProfileService(SportProfileRepository(db), UserRepository(db))
    return sport_service.get_sport_profiles_by_user(current_user.id)


@router.get("/{id}", response_model=SportProfileResponse)
def get_sport_profile(id: int, current_user: User = Depends(require_admin),
                      db: Session = Depends(get_db)) -> SportProfileResponse:
    sport_service = SportProfileService(SportProfileRepository(db), UserRepository(db))
    return sport_service.get_sport_profile(id)


@router.patch("/{id}", response_model=SportProfileResponse)
def update_sport_profile(id: int, sport_data: SportProfileUpdate, current_user: User = Depends(require_admin),
                         db: Session = Depends(get_db)) -> SportProfileResponse:
    sport_service = SportProfileService(SportProfileRepository(db), UserRepository(db))
    return sport_service.update_sport_profile(id, sport_data)


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_sport_profile(id: int, current_user: User = Depends(require_admin),
                         db: Session = Depends(get_db)) -> None:
    sport_service = SportProfileService(SportProfileRepository(db), UserRepository(db))
    sport_service.delete_sport_profile(id)
