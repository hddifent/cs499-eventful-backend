from enum import Enum
from datetime import datetime, UTC
import secrets

from app.core.config import STORAGE_URL

IMG_FILE_EXT = ["png", "jpg", "jpeg"]

class MediaType(Enum):
    USER_PROFILE = "users/pfp"

def media_url(type: MediaType, filename: str) -> str:
    return f"{STORAGE_URL}/media/{type.value}/{filename}"

def media_folder(type: MediaType) -> str:
    return type.value

def media_suffix() -> str:
    timestamp = int(datetime.now(UTC).timestamp())
    random_hex = secrets.token_hex(4)
    return f"{timestamp}_{random_hex}"