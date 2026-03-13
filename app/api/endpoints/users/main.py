from datetime import datetime, timedelta, UTC
from fastapi import APIRouter, status, Request
from sqlalchemy import select, delete

from app.api.types import DBSession
from app.api.schemas import (
    UserCreate,
    UserLogin,
    UserResponse,
    UserProfile
)
from app.api.utils.http_exceptions import (
    EMAIL_ALREADY_REGISTERED,
    USERNAME_ALREADY_REGISTERED,
    INVALID_CREDENTIAL,
    SHOULD_NOT_HAPPEN
)
from app.api.utils.user_dependency import LoggedInUID
from app.api.utils.media import MediaType, media_url
from app.api.endpoints.users import media
from app.db.models import User, Session
from app.core.config import settings
from app.core.security import (
    hash_password,
    verify_password,
    generate_session_tokens,
    hash_session_secret,
    break_session_token
)

router = APIRouter()
router.include_router(media.router, prefix="/media")

@router.post(
    "/register",
    status_code=status.HTTP_201_CREATED,
    response_model=UserResponse
)
async def create_user(data: UserCreate, db: DBSession):
    q_existing_umail = (
        select(User.user_id)
        .where(User.user_email == data.user_email)
        .limit(1)
    )
    r_existing_umail = await db.execute(q_existing_umail)
    s_existing_umail = r_existing_umail.scalar_one_or_none()
    if s_existing_umail != None:
        raise EMAIL_ALREADY_REGISTERED
    
    q_existing_uname = (
        select(User.user_id)
        .where(User.username == data.username)
        .limit(1)
    )
    r_existing_uname = await db.execute(q_existing_uname)
    s_existing_uname = r_existing_uname.scalar_one_or_none()
    if s_existing_uname != None:
        raise USERNAME_ALREADY_REGISTERED
    
    hashed_pwd = hash_password(data.user_pwd)

    new_user = User(
        user_email=data.user_email,
        username=data.username,
        user_display_name=data.user_display_name,
        user_pwd=hashed_pwd
    )

    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    return new_user

@router.post(
    "/login",
    status_code=status.HTTP_200_OK
)
async def login(data: UserLogin, db: DBSession):
    q_user = (
        select(User.user_id, User.user_pwd)
        .where(User.username == data.username)
        .limit(1)
    )
    r_user = await db.execute(q_user)
    row_user = r_user.first()

    if (row_user == None):
        raise INVALID_CREDENTIAL
    
    f_user_id, f_user_pwd = row_user.tuple()

    if (not verify_password(data.user_pwd, f_user_pwd)):
        raise INVALID_CREDENTIAL
    
    session_id, session_raw_secret = generate_session_tokens()
    session_hashed_secret = hash_session_secret(session_raw_secret)

    now = datetime.now(UTC)
    user_session = Session(
        session_id=session_id,
        session_secret=session_hashed_secret,
        created_at=now,
        expire_window=now + timedelta(seconds=settings.SESSION_TIMEOUT),
        expire_absolute=now + timedelta(seconds=settings.ABSOLUTE_TIMEOUT),
        user_id=f_user_id
    )
    
    db.add(user_session)
    await db.commit()

    return {
        "message": "Login successful",
        "session_token": f"{session_id}.{session_raw_secret}",
        "session_maxage": settings.ABSOLUTE_TIMEOUT
    }

@router.post("/logout", status_code=status.HTTP_200_OK)
async def logout(req: Request, db: DBSession):
    req_session_token = req.cookies.get("session_token")
    req_session_tuple = break_session_token(req_session_token)
    if (req_session_tuple != None):
        req_session_id, _ = req_session_tuple
        q_delete = (
            delete(Session)
            .where(Session.session_id == req_session_id)
        )
        await db.execute(q_delete)
        await db.commit()
    
    return {
        "message": "Logout successful."
    }

@router.get(
    "/me",
    status_code=status.HTTP_200_OK,
    response_model=UserProfile
)
async def get_profile(uid: LoggedInUID, db: DBSession):
    q_profile = (
        select(
            User.username,
            User.user_display_name,
            User.user_pfp_suffix
        )
        .where(User.user_id == uid)
        .limit(1)
    )
    r_profile = await db.execute(q_profile)
    row_profile = r_profile.first()

    if (row_profile == None):
        raise SHOULD_NOT_HAPPEN # as uid is a dependency
    
    f_uname, f_disp, f_pfp_suf = row_profile.tuple()
    pfp_url = (
        media_url(MediaType.USER_PROFILE, f"{f_uname}_{f_pfp_suf}")
        if f_pfp_suf != None
        else ""
    )

    return UserProfile(
        username=f_uname,
        user_display_name=f_disp,
        pfp_url=pfp_url
    )
