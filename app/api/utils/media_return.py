from enum import Enum

from app.core.config import STORAGE_URL

class MediaType(Enum):
    USER_PROFILE = "users/pfp"

def media_url(type: MediaType, filename: str) -> str:
    return f"{STORAGE_URL}/{type.value}/{filename}"
