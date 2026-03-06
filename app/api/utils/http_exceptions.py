from fastapi import status, HTTPException

EMAIL_ALREADY_REGISTERED = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail="This email has already been registered."
)

USERNAME_ALREADY_REGISTERED = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail="User with this username already existed."
)

INVALID_CREDENTIAL = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Incorrect username or password."
)

INVALID_SESSION = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Invalid session."
)