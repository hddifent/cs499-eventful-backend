import re

from pydantic import Field

# REGEX --------------------------------------------------------------------------------------------

USERNAME_LIKE_REGEX = re.compile(r"^[a-zA-Z](?!.*[_.]{2})[a-zA-Z0-9_.]*$")
DISPLAY_NAME_LIKE_REGEX = r"^[a-zA-Z0-9_. -]+$"

# FIELD --------------------------------------------------------------------------------------------

USERNAME_LIKE_FIELD = Field(
    min_length=1,
    max_length=32,
    pattern=USERNAME_LIKE_REGEX,
    description="Must start with a letter, no consecutive punctuation, allows letters, numbers, underscores, and periods.",
)

DISPLAY_NAME_LIKE_FIELD = Field(
    min_length=1,
    max_length=100,
    pattern=DISPLAY_NAME_LIKE_REGEX,
    description="Allows alphanumeric characters, spaces, hyphens, periods, and underscores.",
)

PASSWORD_LIKE_FIELD = Field(min_length=8, max_length=64)
