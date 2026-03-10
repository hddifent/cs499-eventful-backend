from fastapi import Depends, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated

from app.core.database import get_db

DBSession = Annotated[AsyncSession, Depends(get_db)]
ReqUploadFile = Annotated[UploadFile, File(...)]
