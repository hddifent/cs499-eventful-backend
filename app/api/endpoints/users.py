from fastapi import APIRouter, status, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from typing import Annotated

from app.schemas import UserCreate, UserLogin, UserResponse

from app.core.database import get_db
from app.db.models import User, Session
from app.core.security import hash_password, verify_password, generate_session_tokens, hash_session_secret

from datetime import datetime, timedelta, UTC

router = APIRouter()

DBSession = Annotated[AsyncSession, Depends(get_db)]

@router.post("/register", status_code=status.HTTP_201_CREATED, response_model=UserResponse)
async def create_user(data: UserCreate, db: DBSession):
    q_existing_umail = select(User).where(User.user_email == data.user_email).limit(1)
    r_existing_umail = await db.execute(q_existing_umail)
    s_existing_umail = r_existing_umail.scalar_one_or_none()
    if s_existing_umail != None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This email has already been registered."
        )
    
    q_existing_uname = select(User).where(User.username == data.username).limit(1)
    r_existing_uname = await db.execute(q_existing_uname)
    s_existing_uname = r_existing_uname.scalar_one_or_none()
    if s_existing_uname != None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this username already existed."
        )
    
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

@router.post("/login", status_code=status.HTTP_200_OK)
async def login(data: UserLogin, db: DBSession):
    q_user = select(User.user_id, User.user_pwd).where(User.username == data.username).limit(1)
    r_user = await db.execute(q_user)
    row_user = r_user.first()

    if (row_user == None) or (not verify_password(data.user_pwd, row_user.user_pwd)):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password."
        )
    
    session_id, session_raw_secret = generate_session_tokens()
    session_hashed_secret = hash_session_secret(session_raw_secret)

    now = datetime.now(UTC)
    user_session = Session(
        session_id=session_id,
        session_secret=session_hashed_secret,
        created_at=now,
        expire_window=now + timedelta(minutes=15),
        expire_absolute=now + timedelta(hours=12),
        user_id=row_user.user_id
    )
    
    db.add(user_session)
    await db.commit()

    return {
        "message": "Login successful",
        "session_token": f"{session_id}.{session_raw_secret}"
    }
