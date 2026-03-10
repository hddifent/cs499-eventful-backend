from typing import Annotated

from fastapi import Request, Depends
from sqlalchemy import select

from app.core.config import settings
from app.core.security import verify_session_token, break_session_token
from app.db.models import Session
from app.api.utils.http_exceptions import INVALID_SESSION
from app.api.types import DBSession

from datetime import datetime, timedelta, UTC

async def get_current_user_id(req: Request, db: DBSession) -> int:
    req_session_token = req.cookies.get("session_token")
    req_session_tuple = break_session_token(req_session_token)
    if (req_session_tuple == None):
        raise INVALID_SESSION
    
    req_session_id, req_session_raw_secret = req_session_tuple
    
    q_session = (
        select(Session)
        .where(Session.session_id == req_session_id)
        .limit(1)
    )
    r_session = await db.execute(q_session)
    s_session = r_session.scalar_one_or_none()

    if (s_session == None):
        raise INVALID_SESSION

    if not verify_session_token(req_session_raw_secret, s_session.session_secret):
        raise INVALID_SESSION
    
    session_expired, session_needs_renewal = _check_session_expiration(s_session)

    if session_expired:
        await db.delete(s_session)
        await db.commit()
        raise INVALID_SESSION
    
    if session_needs_renewal:
        s_session.expire_window = datetime.now(UTC) + timedelta(seconds=settings.SESSION_TIMEOUT)
        await db.commit()
    
    return s_session.user_id

def _check_session_expiration(session: Session) -> tuple[bool, bool]:
    now = datetime.now(UTC)
    if (now >= session.expire_window) or (now >= session.expire_absolute):
        return True, False
    
    if (session.expire_window - now <= timedelta(seconds=settings.SESSION_RENEWAL_THRESHOLD)):
        return False, True
    
    return False, False

LoggedInUID = Annotated[int, Depends(get_current_user_id)]
