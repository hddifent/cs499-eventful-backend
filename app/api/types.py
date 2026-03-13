from typing import Annotated

from fastapi import Depends, File, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db

DBSession = Annotated[AsyncSession, Depends(get_db)]
ReqUploadFile = Annotated[UploadFile, File(...)]
