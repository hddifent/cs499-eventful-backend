from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select

from app.api.types import DBSession, LoggedInUID
from app.api.utils.http_exceptions import SHOULD_NOT_HAPPEN, FILE_NOT_FOUND
from app.api.utils.media_return import MediaType, media_url
from app.db.models import User

router = APIRouter()

@router.get(
    "/profilepic",
    status_code=status.HTTP_200_OK
)
async def fetch_pfp_from_uid(uid: LoggedInUID, db: DBSession):
    q_link_part = (
        select(User.username, User.user_pfp_suffix)
        .where(User.user_id == uid)
        .limit(1)
    )
    r_link_part = await db.execute(q_link_part)
    row_link_part = r_link_part.first()

    if row_link_part == None:
        raise SHOULD_NOT_HAPPEN # as uid is a dependency
    
    f_username, f_suffix = row_link_part.tuple()
    
    if f_suffix == None:
        raise FILE_NOT_FOUND
    
    return {
        "url": media_url(MediaType.USER_PROFILE, f"{f_username}_{f_suffix}")
    }

@router.get(
    "/profilepic/{username}",
    status_code=status.HTTP_200_OK
)
async def fetch_pfp_from_username(username: str, db: DBSession):
    q_suffix = (
        select(User.user_pfp_suffix)
        .where(User.username == username)
        .limit(1)
    )
    r_suffix = await db.execute(q_suffix)
    s_suffix = r_suffix.scalar_one_or_none()

    if s_suffix == None:
        raise FILE_NOT_FOUND
    
    return {
        "url": media_url(MediaType.USER_PROFILE, f"{username}_{s_suffix}")
    }
