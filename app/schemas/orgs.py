from pydantic import BaseModel

from app.schemas.regex_field_util import (
    DISPLAY_NAME_LIKE_FIELD,
    USERNAME_LIKE_FIELD,
)


class OrgCreate(BaseModel):
    org_unique_name: str = USERNAME_LIKE_FIELD
    org_display_name: str = DISPLAY_NAME_LIKE_FIELD
