import json
import re
import secrets
from zoneinfo import ZoneInfo

import httpx
from fastapi import APIRouter, File, Form, HTTPException, UploadFile, status
from pydantic import ValidationError
from sqlalchemy import select
from sqlalchemy.orm.strategy_options import selectinload

from app.api.types import DBSession
from app.api.utils.http_exceptions import (
    BAD_FILE_TYPE,
    BAD_REQUEST,
    EVENT_NOT_FOUND,
    FORBIDDEN,
    INTERNAL_LOGIC_ERROR,
    INTERNAL_SERVER_ERROR,
)
from app.api.utils.media import IMG_FILE_EXT, MediaType, media_folder, media_suffix, media_url
from app.api.utils.org_dependency import AuthorizedOrgID, JoinedOrgList
from app.core.config import STORAGE_URL, settings
from app.db.models import Event, EventDay, EventPublicationStatus
from app.schemas.events import (
    BoothData,
    CreateEventResponse,
    EventCreate,
    EventPrivatePageResponse,
)

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
    response_model=CreateEventResponse,
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


@router.get(
    "/info/{event_slug}/full",
    status_code=status.HTTP_200_OK,
    response_model=EventPrivatePageResponse,
)
async def get_full_event_info(event_slug: str, db: DBSession, org_ids: JoinedOrgList):
    try:
        safe_name, suffix = event_slug.rsplit("-", 1)
    except ValueError:
        raise BAD_REQUEST

    q_event = (
        select(Event)
        .options(selectinload(Event.event_days))
        .where(Event.event_safe_name == safe_name, Event.event_suffix == suffix)
        .limit(1)
    )
    r_event = await db.execute(q_event)
    s_event = r_event.scalar_one_or_none()

    if s_event == None:
        raise EVENT_NOT_FOUND

    if s_event.event_org_id not in org_ids:
        raise FORBIDDEN

    return s_event


@router.patch(
    "/general/{event_slug}",
    status_code=status.HTTP_200_OK,
    response_model=EventPrivatePageResponse,
)
async def update_event(event_slug: str, data: EventCreate, org_id: AuthorizedOrgID, db: DBSession):
    try:
        safe_name, suffix = event_slug.rsplit("-", 1)
    except ValueError:
        raise BAD_REQUEST

    q_existing_event = (
        select(Event)
        .options(selectinload(Event.event_days))
        .where(
            Event.event_safe_name == safe_name,
            Event.event_suffix == suffix,
            Event.event_org_id == org_id,
        )
    )
    r_existing_event = await db.execute(q_existing_event)
    s_existing_event = r_existing_event.scalar_one_or_none()

    if s_existing_event == None:
        raise EVENT_NOT_FOUND

    s_existing_event.event_name = data.event_name
    s_existing_event.event_description = data.event_desc
    s_existing_event.event_location = data.event_loc
    s_existing_event.event_application_info = str(data.event_application_link)
    s_existing_event.event_application_accept_start = data.application_period_start
    s_existing_event.event_application_accept_end = data.application_period_end

    for old_day in s_existing_event.event_days:
        await db.delete(old_day)

    for day in data.event_days:
        try:
            tz = ZoneInfo(day.timezone)
        except Exception:
            raise HTTPException(status_code=400, detail=f"Invalid timezone: {day.timezone}")

        local_start = day.start.astimezone(tz)
        local_end = day.end.astimezone(tz)

        new_day = EventDay(
            belong_in_event_id=s_existing_event.event_id,
            eventday_date=local_start.date(),
            eventday_time_start=local_start.time(),
            eventday_time_end=local_end.time(),
            eventday_timezone=day.timezone,
        )
        db.add(new_day)

    await db.commit()
    await db.refresh(s_existing_event)

    return s_existing_event


@router.patch(
    "/map/{event_slug}",
    status_code=status.HTTP_200_OK,
    response_model=EventPrivatePageResponse,
)
async def update_event_map(
    event_slug: str,
    org_ids: JoinedOrgList,
    db: DBSession,
    data: str = Form(...),
    file: UploadFile = File(...),
):
    if file.filename == None:
        raise BAD_REQUEST

    _, file_ext = file.filename.rsplit(".", 1)
    if file_ext not in IMG_FILE_EXT:
        raise BAD_FILE_TYPE

    try:
        safe_name, suffix = event_slug.rsplit("-", 1)
    except ValueError:
        raise BAD_REQUEST

    try:
        raw_dict = json.loads(data)
        parsed_booth_data = {label: BoothData(**booth) for label, booth in raw_dict.items()}
    except (json.JSONDecodeError, ValidationError) as _:
        raise BAD_REQUEST

    q_existing_event = (
        select(Event)
        .options(selectinload(Event.event_days))
        .where(
            Event.event_safe_name == safe_name,
            Event.event_suffix == suffix,
        )
    )
    r_existing_event = await db.execute(q_existing_event)
    s_existing_event = r_existing_event.scalar_one_or_none()

    if s_existing_event == None:
        raise EVENT_NOT_FOUND

    if s_existing_event.event_org_id not in org_ids:
        raise FORBIDDEN

    file_suffix_m = f"{media_suffix()}.{file_ext}"
    file_bytes_m = await file.read()

    req_folder_m = media_folder(MediaType.EVENT_MAP)
    req_filename_m = f"{event_slug}_{file_suffix_m}"

    async with httpx.AsyncClient() as cli:
        res = await cli.post(
            f"{STORAGE_URL}/upload",
            headers={"EVT-Media-Token": settings.STORAGE_SKEY},
            data={"folder": req_folder_m},
            files={"file": (req_filename_m, file_bytes_m, file.content_type)},
        )

    if res.is_error:
        raise INTERNAL_SERVER_ERROR

    res_data = res.json()
    if res_data["location"] == None:
        raise INTERNAL_SERVER_ERROR

    map_url = media_url(MediaType.EVENT_MAP, req_filename_m)

    if not map_url.endswith(res_data["location"]):
        raise INTERNAL_LOGIC_ERROR

    booth_dict = {label: booth.model_dump() for label, booth in parsed_booth_data.items()}

    file_suffix_d = f"{media_suffix()}.json"
    req_folder_d = media_folder(MediaType.EVENT_MAP_DISPLAY_DATA)
    req_filename_d = f"{event_slug}_{file_suffix_d}"
    file_bytes_d = json.dumps(booth_dict).encode("utf-8")

    async with httpx.AsyncClient() as cli:
        res_json = await cli.post(
            f"{STORAGE_URL}/upload",
            headers={"EVT-Media-Token": settings.STORAGE_SKEY},
            data={"folder": req_folder_d},
            files={"file": (req_filename_d, file_bytes_d, "application/json")},
        )

    if res_json.is_error:
        raise INTERNAL_SERVER_ERROR

    res_json_data = res_json.json()
    if res_json_data.get("location") is None:
        raise INTERNAL_SERVER_ERROR

    map_data_url = media_url(MediaType.EVENT_MAP_DISPLAY_DATA, req_filename_d)

    if not map_data_url.endswith(res_json_data["location"]):
        raise INTERNAL_LOGIC_ERROR

    s_existing_event.event_map_img_suffix = file_suffix_m
    s_existing_event.event_map_data_suffix = file_suffix_d

    await db.commit()
    await db.refresh(s_existing_event)

    return s_existing_event
