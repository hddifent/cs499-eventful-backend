from pydantic import BaseModel, ConfigDict, Field, EmailStr

# -- Users --
class UserBase(BaseModel): # Not sure what to do yet...
    username: str = Field(min_length=1, max_length=32)

class UserCreate(UserBase):
    user_email: EmailStr
    user_display_name: str = Field(min_length=1, max_length=100)
    user_pwd: str = Field(min_length=8, max_length=64)

class UserLogin(UserBase):
    user_pwd: str = Field(min_length=1)

# TODO: Mocking a lot of stuffs rn. Fix me pls.
# -- Events --
class EventBase(BaseModel):
    title: str = Field(min_length=1, max_length=256)
    description: str = Field(default="")