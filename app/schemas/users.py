from pydantic import BaseModel, EmailStr

from app.schemas.orgs import OrgPagePublicResponse
from app.schemas.regex_field_util import (
    DISPLAY_NAME_LIKE_FIELD,
    PASSWORD_LIKE_FIELD,
    USERNAME_LIKE_FIELD,
)
from app.schemas.shared_base import UserResponse


# REQUEST SCHEMAS ----------------------------------------------------------------------------------
class UserCreate(BaseModel):
    username: str = USERNAME_LIKE_FIELD
    user_email: EmailStr
    user_display_name: str = DISPLAY_NAME_LIKE_FIELD
    user_pwd: str = PASSWORD_LIKE_FIELD


class UserLogin(BaseModel):
    username: str = USERNAME_LIKE_FIELD
    user_pwd: str = PASSWORD_LIKE_FIELD


# RESPONSE SCHEMAS ---------------------------------------------------------------------------------
class UserPublicProfile(UserResponse):
    pfp_url: str


class UserPrivateProfile(UserPublicProfile):
    user_orgs_invited: list[OrgPagePublicResponse]
    user_orgs_joined: list[OrgPagePublicResponse]
