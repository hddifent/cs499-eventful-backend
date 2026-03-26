import re
import secrets
from zoneinfo import ZoneInfo

from fastapi import APIRouter, HTTPException, status

from app.api.types import DBSession
from app.api.utils.org_dependency import AuthorizedOrgID
from app.db.models import Event, EventDay, EventPublicationStatus
from app.schemas.events import EventCreate, EventResponse

router = APIRouter()


def _generate_slug(text: str) -> str:
    """Converts a string into a URL-friendly slug."""
    text = text.lower()
    return re.sub(r"[^a-z0-9]+", "-", text).strip("-")


@router.get("/")
def get_events():
    return []


@router.post(
    "/new",
    status_code=status.HTTP_201_CREATED,
    response_model=EventResponse,
)
async def create_new_event(data: EventCreate, org_id: AuthorizedOrgID, db: DBSession):
    safe_name = _generate_slug(data.event_name)
    suffix = secrets.token_hex(4)

    new_event = Event(
        event_org_id=org_id,
        event_name=data.event_name,
        event_safe_name=safe_name,
        event_suffix=suffix,
        event_description=data.event_desc,
        event_location=data.event_loc,
        event_application_info=str(data.event_application_link),
        event_application_accept_start=data.application_period_start,
        event_application_accept_end=data.application_period_end,
        event_publication_status=EventPublicationStatus.DRAFT,
    )

    db.add(new_event)
    await db.flush()

    for day in data.event_days:
        try:
            tz = ZoneInfo(day.timezone)
        except Exception:
            raise HTTPException(status_code=400, detail=f"Invalid timezone: {day.timezone}")

        local_start = day.start.astimezone(tz)
        local_end = day.end.astimezone(tz)

        new_day = EventDay(
            belong_in_event_id=new_event.event_id,
            eventday_date=local_start.date(),
            eventday_time_start=local_start.time(),
            eventday_time_end=local_end.time(),
            eventday_timezone=day.timezone,
        )
        db.add(new_day)

    await db.commit()
    await db.refresh(new_event)

    return new_event
