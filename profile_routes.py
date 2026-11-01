
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database import get_db
from models import User, UserProfile, RevokedToken
from schemas import ProfileCreate, ProfileUpdate, ProfileResponse, MessageResponse
from user_routes import get_current_user


router = APIRouter(prefix="/profile", tags=["User Profile"])


# 1. Create User Profile API
@router.post(
    "/",
    response_model=ProfileResponse,
    status_code=status.HTTP_201_CREATED
)
def create_profile(
    profile_data: ProfileCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    existing_profile = db.query(UserProfile).filter(
        UserProfile.user_id == current_user.id
    ).first()

    if existing_profile:
        raise HTTPException(
            status_code=409,
            detail="User profile already exists"
        )

    new_profile = UserProfile(
        user_id=current_user.id,
        **profile_data.model_dump()
    )

    db.add(new_profile)
    db.commit()
    db.refresh(new_profile)

    return new_profile


# 2. Get User Profile API
@router.get(
    "/",
    response_model=ProfileResponse
)
def get_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    profile = db.query(UserProfile).filter(
        UserProfile.user_id == current_user.id
    ).first()

    if not profile:
        raise HTTPException(
            status_code=404,
            detail="User profile not found"
        )

    return profile


# 3. Update User Profile API
@router.put(
    "/",
    response_model=ProfileResponse
)
def update_profile(
    profile_data: ProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    profile = db.query(UserProfile).filter(
        UserProfile.user_id == current_user.id
    ).first()

    if not profile:
        raise HTTPException(
            status_code=404,
            detail="User profile not found"
        )

    update_data = profile_data.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(profile, field, value)

    db.commit()
    db.refresh(profile)

    return profile


# 4. Delete User Account API
@router.delete(
    "/account",
    response_model=MessageResponse
)
def delete_account(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Remove revoked tokens belonging to this user
    db.query(RevokedToken).filter(
        RevokedToken.user_id == current_user.id
    ).delete(synchronize_session=False)

    # Deleting the user also deletes their profile and
    # password reset tokens through ORM relationships.
    db.delete(current_user)
    db.commit()

    return {
        "message": "User account deleted successfully"
    }
