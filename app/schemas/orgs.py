from typing import List

from pydantic import BaseModel, ConfigDict, Field

from app.db.models import OrganizerMemberStatus
from app.schemas.events import EventSummaryWithStatusResponse
from app.schemas.regex_field_util import (
    DISPLAY_NAME_LIKE_FIELD,
    USERNAME_LIKE_FIELD,
)
from app.schemas.shared_base import OrgBase, OrgPagePublicResponse
from app.schemas.users import UserPublicProfile


# REQUEST SCHEMAS ----------------------------------------------------------------------------------
class OrgCreate(OrgBase):
    org_display_name: str = DISPLAY_NAME_LIKE_FIELD


class OrgMemberAction(OrgBase):
    username: str = USERNAME_LIKE_FIELD


# RESPONSE SCHEMAS ---------------------------------------------------------------------------------
class OrgMemberResponse(BaseModel):
    status: OrganizerMemberStatus
    user: UserPublicProfile

    model_config = ConfigDict(from_attributes=True)


class OrgPagePrivateResponse(OrgPagePublicResponse):
    head_user: UserPublicProfile
    org_members: list[OrgMemberResponse]

    org_events: List[EventSummaryWithStatusResponse] = Field(default_factory=list)
