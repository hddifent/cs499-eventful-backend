from pydantic import BaseModel, ConfigDict, EmailStr

from app.schemas.regex_field_util import (
    DISPLAY_NAME_LIKE_FIELD,
    PASSWORD_LIKE_FIELD,
    USERNAME_LIKE_FIELD,
)


class UserCreate(BaseModel):
    username: str = USERNAME_LIKE_FIELD
    user_email: EmailStr
    user_display_name: str = DISPLAY_NAME_LIKE_FIELD
    user_pwd: str = PASSWORD_LIKE_FIELD


class UserLogin(BaseModel):
    username: str = USERNAME_LIKE_FIELD
    user_pwd: str = PASSWORD_LIKE_FIELD


class UserResponse(BaseModel):
    username: str
    user_display_name: str

    model_config = ConfigDict(from_attributes=True)


class UserProfile(UserResponse):
    pfp_url: str
