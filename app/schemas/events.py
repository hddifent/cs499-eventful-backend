from datetime import date, datetime, time
from typing import Dict, List, Optional, Tuple

from fastapi import File, UploadFile
from pydantic import BaseModel, ConfigDict, Field, HttpUrl, Json, computed_field

from app.api.utils.media import MediaType, media_url
from app.db.models import EventPublicationStatus
from app.schemas.orgs import OrgBase
from app.schemas.regex_field_util import DISPLAY_NAME_LIKE_FIELD


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


class EventPrivatePageResponse(CreateEventResponse):
    event_name: str
    event_description: Optional[str]
    event_location: Optional[str]
    event_application_info: Optional[str]
    event_application_accept_start: Optional[datetime]
    event_application_accept_end: Optional[datetime]
    event_publication_status: EventPublicationStatus
    event_days: List[EventDayResponse]

    event_map_img_suffix: Optional[str] = None
    event_map_data_suffix: Optional[str] = None

    @computed_field
    def event_map_url(self) -> Optional[str]:
        if not self.event_map_img_suffix:
            return None
        filename = f"{self.event_slug}_{self.event_map_img_suffix}"
        return media_url(MediaType.EVENT_MAP, filename)

    @computed_field
    def event_map_data_url(self) -> Optional[str]:
        if not self.event_map_data_suffix:
            return None
        filename = f"{self.event_slug}_{self.event_map_data_suffix}"
        return media_url(MediaType.EVENT_MAP_DISPLAY_DATA, filename)

    model_config = ConfigDict(from_attributes=True)
