from datetime import date, datetime, time
from typing import Dict, List, Optional, Tuple

from fastapi import File, UploadFile
from pydantic import BaseModel, ConfigDict, Field, HttpUrl, Json, computed_field

from app.api.utils.media import MediaType, media_url
from app.db.models import EventPublicationStatus
from app.schemas.orgs import OrgBase
from app.schemas.regex_field_util import DISPLAY_NAME_LIKE_FIELD
from app.schemas.users import UserPublicProfile


# REQUEST SCHEMAS ----------------------------------------------------------------------------------
class EventDayBase(BaseModel):
    start: datetime
    end: datetime
    timezone: str


class EventCreate(OrgBase):
    event_name: str = DISPLAY_NAME_LIKE_FIELD
    event_desc: str = Field(min_length=1)
    event_loc: str = Field(min_length=1, max_length=256)
    event_application_link: HttpUrl | str
    application_period_start: datetime
    application_period_end: datetime
    event_days: List[EventDayBase] = Field(min_length=1)


class BoothData(BaseModel):
    bounding_box: Tuple[Tuple[int, int], Tuple[int, int]]


# RESPONSE SCHEMAS ---------------------------------------------------------------------------------
class CreateEventResponse(BaseModel):
    event_safe_name: str = Field(exclude=True)
    event_suffix: str = Field(exclude=True)

    @computed_field
    def event_slug(self) -> str:
        return f"{self.event_safe_name}-{self.event_suffix}"


class EventDayResponse(BaseModel):
    eventday_date: date
    eventday_time_start: time
    eventday_time_end: time
    eventday_timezone: str

    model_config = ConfigDict(from_attributes=True)


class ApplicationPublicResponse(BaseModel):
    assigned_booth: Optional[str] = None
    user: UserPublicProfile

    model_config = ConfigDict(from_attributes=True)


class ApplicationPrivateResponse(ApplicationPublicResponse):
    status: str


class EventPublicPageResponse(CreateEventResponse):
    event_name: str
    event_description: Optional[str]
    event_location: Optional[str]
    event_application_info: Optional[str]
    event_application_accept_start: Optional[datetime]
    event_application_accept_end: Optional[datetime]
    event_days: List[EventDayResponse]

    applications: List[ApplicationPrivateResponse] = Field(exclude=True, default_factory=list)

    event_map_img_suffix: Optional[str] = Field(exclude=True, default=None)
    event_map_data_suffix: Optional[str] = Field(exclude=True, default=None)

    @computed_field
    def accepted_booths(self) -> List[ApplicationPublicResponse]:
        return [
            ApplicationPublicResponse(assigned_booth=app.assigned_booth, user=app.user)
            for app in self.applications
            if app.status == "ACCEPTED" and app.assigned_booth is not None
        ]

    @computed_field
    def event_map_url(self) -> Optional[str]:
        if not self.event_map_img_suffix:
            return None
        return media_url(MediaType.EVENT_MAP, f"{self.event_slug}_{self.event_map_img_suffix}")

    @computed_field
    def event_map_data_url(self) -> Optional[str]:
        if not self.event_map_data_suffix:
            return None
        return media_url(
            MediaType.EVENT_MAP_DISPLAY_DATA, f"{self.event_slug}_{self.event_map_data_suffix}"
        )

    model_config = ConfigDict(from_attributes=True)


class EventPrivatePageResponse(EventPublicPageResponse):
    event_publication_status: EventPublicationStatus
