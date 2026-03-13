import re

from pydantic import BaseModel, ConfigDict, EmailStr, Field

# -- Users --

_USERNAME_FIELD = Field(
    min_length=1,
    max_length=32,
    pattern=re.compile(r"^[a-zA-Z](?!.*[_.]{2})[a-zA-Z0-9_.]*$"),
    description="Must start with a letter, no consecutive punctuation, allows letters, numbers, underscores, and periods.",
)

_DISPLAY_NAME_FIELD = Field(
    min_length=1,
    max_length=100,
    pattern=r"^[a-zA-Z0-9_. -]+$",
    description="Allows alphanumeric characters, spaces, hyphens, periods, and underscores.",
)

_PASSWORD_FIELD = Field(min_length=8, max_length=64)


class UserCreate(BaseModel):
    username: str = _USERNAME_FIELD
    user_email: EmailStr
    user_display_name: str = _DISPLAY_NAME_FIELD
    user_pwd: str = _PASSWORD_FIELD


class UserLogin(BaseModel):
    username: str = _USERNAME_FIELD
    user_pwd: str = _PASSWORD_FIELD


class UserResponse(BaseModel):
    username: str
    user_display_name: str

    model_config = ConfigDict(from_attributes=True)


class UserProfile(UserResponse):
    pfp_url: str


# TODO: Mocking a lot of stuffs rn. Fix me pls.
# -- Events --
class EventBase(BaseModel):
    title: str = Field(min_length=1, max_length=256)
    description: str = Field(default="")
