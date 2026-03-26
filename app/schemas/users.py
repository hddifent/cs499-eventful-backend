from datetime import date
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field, computed_field

from app.api.utils.media import MediaType, media_url
from app.db.models import OrganizerMemberStatus
from app.schemas.regex_field_util import (
    DISPLAY_NAME_LIKE_FIELD,
    PASSWORD_LIKE_FIELD,
    USERNAME_LIKE_FIELD,
)
from app.schemas.shared_base import OrgPagePublicResponse, UserResponse


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
class AcceptedEventItem(BaseModel):
    event_name: str
    event_slug: str
    assigned_booth: str
    start_date: date
    end_date: date


class _UserEventDayResponse(BaseModel):
    eventday_date: date
    model_config = ConfigDict(from_attributes=True)


class _UserEventResponse(BaseModel):
    event_name: str
    event_safe_name: str
    event_suffix: str
    event_days: List[_UserEventDayResponse] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)


class _UserApplicationResponse(BaseModel):
    status: str
    assigned_booth: Optional[str] = None
    event: _UserEventResponse

    model_config = ConfigDict(from_attributes=True)


class UserMembershipResponse(BaseModel):
    status: OrganizerMemberStatus
    org: OrgPagePublicResponse

    model_config = ConfigDict(from_attributes=True)


class UserPublicProfile(UserResponse):
    user_pfp_suffix: str | None = Field(default=None, exclude=True)

    @computed_field
    def pfp_url(self) -> str:
        if self.user_pfp_suffix:
            return media_url(MediaType.USER_PROFILE, f"{self.username}_{self.user_pfp_suffix}")
        return ""


class UserPrivateProfile(UserPublicProfile):
    user_org_memberships: list[UserMembershipResponse] = Field(default_factory=list, exclude=True)
    event_applications: list[_UserApplicationResponse] = Field(default_factory=list, exclude=True)

    @computed_field
    def user_orgs_invited(self) -> list[OrgPagePublicResponse]:
        return [
            m.org for m in self.user_org_memberships if m.status == OrganizerMemberStatus.INVITED
        ]

    @computed_field
    def user_orgs_joined(self) -> list[OrgPagePublicResponse]:
        return [
            m.org for m in self.user_org_memberships if m.status == OrganizerMemberStatus.JOINED
        ]

    @computed_field
    def user_accepted_events(self) -> list[AcceptedEventItem]:
        res = []
        for app in self.event_applications:
            if app.status == "ACCEPTED" and app.assigned_booth and app.event.event_days:
                days = sorted([d.eventday_date for d in app.event.event_days])
                res.append(
                    AcceptedEventItem(
                        event_name=app.event.event_name,
                        event_slug=f"{app.event.event_safe_name}-{app.event.event_suffix}",
                        assigned_booth=app.assigned_booth,
                        start_date=days[0],
                        end_date=days[-1],
                    )
                )
        return res
