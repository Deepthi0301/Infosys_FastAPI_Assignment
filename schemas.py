
from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import Optional


# Common configuration for database response schemas
class ORMBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)


# 1. User Registration
class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


# 2. User Login
class UserLogin(BaseModel):
    email: EmailStr
    password: str


# 3. Token Response
class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


# 4. User Response
class UserResponse(ORMBase):
    id: int
    email: EmailStr
    is_active: bool


# 5. Create User Profile
class ProfileCreate(BaseModel):
    full_name: str = Field(min_length=2, max_length=150)
    phone: Optional[str] = Field(default=None, max_length=20)
    address: Optional[str] = None
    linkedin: Optional[str] = None
    github: Optional[str] = None
    professional_summary: Optional[str] = None


# 6. Update User Profile
class ProfileUpdate(BaseModel):
    full_name: Optional[str] = Field(default=None, min_length=2, max_length=150)
    phone: Optional[str] = Field(default=None, max_length=20)
    address: Optional[str] = None
    linkedin: Optional[str] = None
    github: Optional[str] = None
    professional_summary: Optional[str] = None


# 7. Get User Profile Response
class ProfileResponse(ORMBase):
    id: int
    user_id: int
    full_name: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    linkedin: Optional[str] = None
    github: Optional[str] = None
    professional_summary: Optional[str] = None


# 8. Forgot Password
class ForgotPasswordRequest(BaseModel):
    email: EmailStr


# 9. Reset Password
class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str = Field(min_length=8, max_length=128)


# 10. Change Password
class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str = Field(min_length=8, max_length=128)


# 11. General API Message
class MessageResponse(BaseModel):
    message: str


class ForgotPasswordResponse(BaseModel):
    message: str
    reset_token: Optional[str] = None
