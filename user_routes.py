
import secrets
import hashlib
import os

from datetime import datetime, timedelta, timezone

from models import PasswordResetToken
from schemas import (
    ForgotPasswordRequest,
    ForgotPasswordResponse,
    ResetPasswordRequest,
    ChangePasswordRequest
)

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from database import get_db
from models import User, RevokedToken
from schemas import UserCreate, UserLogin, UserResponse, TokenResponse, MessageResponse
from auth import hash_password, verify_password, create_access_token, decode_access_token


router = APIRouter(prefix="/auth", tags=["User Authentication"])

security = HTTPBearer()


# Verify JWT and identify logged-in user
def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    token = credentials.credentials
    payload = decode_access_token(token)

    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired access token"
        )

    user_id = payload.get("sub")
    jti = payload.get("jti")

    if not user_id or not jti:
        raise HTTPException(
            status_code=401,
            detail="Invalid access token"
        )

    # Check whether the token has been revoked
    revoked = db.query(RevokedToken).filter(
        RevokedToken.jti == jti
    ).first()

    if revoked:
        raise HTTPException(
            status_code=401,
            detail="Token has been revoked. Please login again."
        )

    user = db.query(User).filter(
        User.id == int(user_id),
        User.is_active == True
    ).first()

    if not user:
        raise HTTPException(
            status_code=401,
            detail="User not found or inactive"
        )

    return user


# 1. User Registration API
@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED
)
def register_user(
    user_data: UserCreate,
    db: Session = Depends(get_db)
):
    existing_user = db.query(User).filter(
        User.email == user_data.email
    ).first()

    if existing_user:
        raise HTTPException(
            status_code=409,
            detail="Email is already registered"
        )

    new_user = User(
        email=user_data.email,
        hashed_password=hash_password(user_data.password)
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


# 2. User Login API
@router.post(
    "/login",
    response_model=TokenResponse
)
def login_user(
    login_data: UserLogin,
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(
        User.email == login_data.email
    ).first()

    if not user or not verify_password(
        login_data.password,
        user.hashed_password
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    if not user.is_active:
        raise HTTPException(
            status_code=403,
            detail="User account is inactive"
        )

    access_token = create_access_token(
        data={"sub": str(user.id)}
    )

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }


# 3. User Logout API
@router.post(
    "/logout",
    response_model=MessageResponse
)
def logout_user(
    current_user: User = Depends(get_current_user),
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    payload = decode_access_token(credentials.credentials)
    jti = payload.get("jti")

    already_revoked = db.query(RevokedToken).filter(
        RevokedToken.jti == jti
    ).first()

    if not already_revoked:
        revoked_token = RevokedToken(
            jti=jti,
            user_id=current_user.id
        )

        db.add(revoked_token)
        db.commit()

    return {"message": "Successfully logged out"}


# Helper: Hash reset token using SHA-256
def hash_reset_token(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


# 4. Forgot Password API
@router.post(
    "/forgot-password",
    response_model=ForgotPasswordResponse
)
def forgot_password(
    request: ForgotPasswordRequest,
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(
        User.email == request.email
    ).first()

    # Do not reveal whether an email is registered
    if not user:
        return {
            "message": "If the account exists, a reset token has been generated."
        }

    # Generate a secure random token
    reset_token = secrets.token_urlsafe(32)

    token_hash = hash_reset_token(reset_token)

    # Token expires after 15 minutes
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=15)

    reset_record = PasswordResetToken(
        user_id=user.id,
        token_hash=token_hash,
        expires_at=expires_at,
        is_used=False
    )

    db.add(reset_record)
    db.commit()

    response = {
        "message": "Password reset token generated successfully."
    }

    # Development-only token for Swagger testing
    if os.getenv("ENVIRONMENT", "development") == "development":
        response["reset_token"] = reset_token

    return response


# 5. Reset Password API
@router.post(
    "/reset-password",
    response_model=MessageResponse
)
def reset_password(
    request: ResetPasswordRequest,
    db: Session = Depends(get_db)
):
    token_hash = hash_reset_token(request.token)

    reset_record = db.query(PasswordResetToken).filter(
        PasswordResetToken.token_hash == token_hash,
        PasswordResetToken.is_used == False
    ).first()

    if not reset_record:
        raise HTTPException(
            status_code=400,
            detail="Invalid or already used reset token"
        )

    # SQLite may return a timezone-naive datetime
    expiry = reset_record.expires_at

    if expiry.tzinfo is None:
        expiry = expiry.replace(tzinfo=timezone.utc)

    if expiry < datetime.now(timezone.utc):
        raise HTTPException(
            status_code=400,
            detail="Reset token has expired"
        )

    user = db.query(User).filter(
        User.id == reset_record.user_id
    ).first()

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    # Update password securely
    user.hashed_password = hash_password(request.new_password)

    # Mark token as used
    reset_record.is_used = True

    db.commit()

    return {
        "message": "Password reset successfully"
    }


# 6. Change Password API
@router.post(
    "/change-password",
    response_model=MessageResponse
)
def change_password(
    request: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Verify current password
    if not verify_password(
        request.current_password,
        current_user.hashed_password
    ):
        raise HTTPException(
            status_code=400,
            detail="Current password is incorrect"
        )

    if request.current_password == request.new_password:
        raise HTTPException(
            status_code=400,
            detail="New password must be different from current password"
        )

    # Hash and update new password
    current_user.hashed_password = hash_password(
        request.new_password
    )

    db.commit()

    return {
        "message": "Password changed successfully"
    }
