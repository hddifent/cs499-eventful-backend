# app/schemas/event.py
from datetime import datetime
from typing import List

from pydantic import BaseModel, Field, HttpUrl, computed_field

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
class EventResponse(BaseModel):
    event_safe_name: str = Field(exclude=True)
    event_suffix: str = Field(exclude=True)

    @computed_field
    def event_slug(self) -> str:
        return f"{self.event_safe_name}-{self.event_suffix}"
