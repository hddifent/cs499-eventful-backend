import httpx
from fastapi import APIRouter, status
from sqlalchemy import select

from app.core.config import STORAGE_URL, settings
from app.api.types import DBSession, ReqUploadFile
from app.api.utils.user_dependency import LoggedInUID
from app.api.utils.http_exceptions import (
    SHOULD_NOT_HAPPEN,
    FILE_NOT_FOUND,
    BAD_REQUEST,
    BAD_FILE_TYPE,
    INTERNAL_SERVER_ERROR,
    INTERNAL_LOGIC_ERROR
)
from app.api.utils.media import (
    IMG_FILE_EXT,
    MediaType,
    media_url,
    media_folder,
    media_suffix
)
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

@router.post(
    "/profilepic",
    status_code=status.HTTP_201_CREATED
)
async def upload_pfp(file: ReqUploadFile, uid: LoggedInUID, db: DBSession):
    if file.filename == None:
        raise BAD_REQUEST

    _, file_ext = file.filename.rsplit(".", 1)
    if file_ext not in IMG_FILE_EXT:
        raise BAD_FILE_TYPE

    q_user = (
        select(User)
        .where(User.user_id == uid)
        .limit(1)
    )
    r_user = await db.execute(q_user)
    s_user = r_user.scalar_one_or_none()

    if s_user == None:
        raise SHOULD_NOT_HAPPEN # as uid is a dependency
    
    file_suffix = f"{media_suffix()}.{file_ext}"
    file_bytes = await file.read()

    req_folder = media_folder(MediaType.USER_PROFILE)
    req_filename = f"{s_user.username}_{file_suffix}"

    async with httpx.AsyncClient() as cli:
        res = await cli.post(
            f"{STORAGE_URL}/upload",
            headers={ "EVT-Media-Token": settings.STORAGE_SKEY },
            data={ "folder": req_folder },
            files={ "file": (
                req_filename,
                file_bytes,
                file.content_type
            )}
        )

    if res.is_error:
        raise INTERNAL_SERVER_ERROR
    
    res_data = res.json()
    if res_data["location"] == None:
        raise INTERNAL_SERVER_ERROR
    
    pfp_url = media_url(MediaType.USER_PROFILE, req_filename)

    if (not pfp_url.endswith(res_data["location"])):
        raise INTERNAL_LOGIC_ERROR
    
    s_user.user_pfp_suffix = file_suffix
    await db.commit()

    return {
        "url": pfp_url
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
