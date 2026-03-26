from datetime import date, datetime, time
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field, HttpUrl, computed_field

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


class EventPrivatePageResponse(BaseModel):
    event_name: str
    event_description: Optional[str]
    event_location: Optional[str]
    event_application_info: Optional[str]
    event_application_accept_start: Optional[datetime]
    event_application_accept_end: Optional[datetime]
    event_publication_status: EventPublicationStatus
    event_days: List[EventDayResponse]

    model_config = ConfigDict(from_attributes=True)
