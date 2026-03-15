from pydantic import BaseModel, ConfigDict

from app.db.models import OrganizerMemberStatus
from app.schemas.regex_field_util import (
    DISPLAY_NAME_LIKE_FIELD,
    USERNAME_LIKE_FIELD,
)
from app.schemas.users import UserResponse


# REQUEST SCHEMAS ----------------------------------------------------------------------------------
class OrgBase(BaseModel):
    org_unique_name: str = USERNAME_LIKE_FIELD


class OrgCreate(OrgBase):
    org_display_name: str = DISPLAY_NAME_LIKE_FIELD


class OrgMemberAction(OrgBase):
    username: str = USERNAME_LIKE_FIELD


# RESPONSE SCHEMAS ---------------------------------------------------------------------------------
class OrgMemberResponse(BaseModel):
    status: OrganizerMemberStatus
    user: UserResponse

    model_config = ConfigDict(from_attributes=True)


class OrgPagePublicResponse(BaseModel):
    org_unique_name: str
    org_display_name: str


class OrgPagePrivateResponse(OrgPagePublicResponse):
    head_user: UserResponse
    org_members: list[OrgMemberResponse]

    model_config = ConfigDict(from_attributes=True)
