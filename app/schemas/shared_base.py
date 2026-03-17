from pydantic import BaseModel, ConfigDict

# This is to prevent cyclic imports


class UserResponse(BaseModel):
    username: str
    user_display_name: str

    model_config = ConfigDict(from_attributes=True)


class OrgPagePublicResponse(BaseModel):
    org_unique_name: str
    org_display_name: str

    model_config = ConfigDict(from_attributes=True)
