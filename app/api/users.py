from fastapi import APIRouter, status, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from typing import Annotated

from app.schemas import UserBase, UserCreate

from app.core.database import get_db
from app.db.models import User
from app.core.security import hash_password

router = APIRouter()

DBSession = Annotated[AsyncSession, Depends(get_db)]

@router.post("/register", status_code=status.HTTP_201_CREATED, response_model=UserBase)
async def create_user(data: UserCreate, db: DBSession):
    existing_umail_q = select(User).where(User.user_email == data.user_email)
    existing_umail = await db.execute(existing_umail_q)

    if existing_umail.scalar_one_or_none() != None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This email has already been registered."
        )
    
    existing_uname_q = select(User).where(User.username == data.username)
    existing_uname = await db.execute(existing_uname_q)

    if existing_uname.scalar_one_or_none() != None:
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
