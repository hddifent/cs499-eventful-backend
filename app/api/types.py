from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated

from app.api.utils.user_dependency import get_current_user_id
from app.core.database import get_db

DBSession = Annotated[AsyncSession, Depends(get_db)]
LoggedInUID = Annotated[int, Depends(get_current_user_id)]
