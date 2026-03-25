from fastapi import HTTPException, status

BAD_REQUEST = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail="Bad request.",
)

EMAIL_ALREADY_REGISTERED = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail="This email has already been registered.",
)

USERNAME_ALREADY_REGISTERED = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail="User with this username already existed.",
)

ORG_UNAME_ALREADY_REGISTERED = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail="Organizer Group with this unique name already existed.",
)

ORG_DNAME_ALREADY_REGISTERED = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail="Organizer Group with this display name already existed.",
)

ORG_ALREADY_INVITED = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail="User has already been invited.",
)

BAD_FILE_TYPE = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail="Bad file type.",
)

INVALID_CREDENTIAL = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Incorrect username or password.",
)

INVALID_SESSION = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Invalid session.",
)

FORBIDDEN = HTTPException(
    status_code=status.HTTP_403_FORBIDDEN,
    detail="Access forbidden.",
)

ORG_INVITATION_NOT_ACCEPTED = HTTPException(
    status_code=status.HTTP_403_FORBIDDEN,
    detail="Access forbidden. However, an invite to this group has been issued to you. Please accept it in your accounts page.",
)

FILE_NOT_FOUND = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail="File not found.",
)

USER_NOT_FOUND = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail="User not found.",
)

ORG_NOT_FOUND = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail="Organizer Group not found.",
)

INTERNAL_SERVER_ERROR = HTTPException(
    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    detail="Internal server error. Operation cannot be completed from connection error.",
)

INTERNAL_LOGIC_ERROR = HTTPException(
    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    detail="Internal server error. Logical error, contact devs.",
)

SHOULD_NOT_HAPPEN = HTTPException(
    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    detail="Internal server error. This error shouldn't happen, contact devs.",
)

NOT_IMPLEMENTED = HTTPException(
    status_code=status.HTTP_501_NOT_IMPLEMENTED,
    detail="Not implemented, contact devs.",
)
