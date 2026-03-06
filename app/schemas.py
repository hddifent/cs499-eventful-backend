from pydantic import BaseModel, ConfigDict, Field, EmailStr
import re

# -- Users --

class UserCreate(BaseModel):
    username: str = Field(
        min_length=1, 
        max_length=32,
        pattern=r"^[a-zA-Z](?!.*[_.]{2})[a-zA-Z0-9_.]*$",
        description="Must start with a letter, no consecutive punctuation, allows letters, numbers, underscores, and periods."
    )

    user_email: EmailStr
    
    user_display_name: str = Field(
        min_length=1, 
        max_length=100,
        pattern=r"^[a-zA-Z0-9_. -]+$",
        description="Allows alphanumeric characters, spaces, hyphens, periods, and underscores."
    )
    
    user_pwd: str = Field(min_length=8, max_length=64)

class UserLogin(BaseModel):
    username: str = Field(min_length=1, max_length=32)
    user_pwd: str = Field(min_length=1)

class UserResponse(BaseModel):
    username: str
    user_display_name: str
    
    model_config = ConfigDict(from_attributes=True)

# TODO: Mocking a lot of stuffs rn. Fix me pls.
# -- Events --
class EventBase(BaseModel):
    title: str = Field(min_length=1, max_length=256)
    description: str = Field(default="")