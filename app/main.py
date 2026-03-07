from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

from app.api.endpoints import process_map, events, users
from app.api.utils.http_exceptions import INVALID_CREDENTIAL

app = FastAPI()

@app.exception_handler(RequestValidationError)
async def req_validate_exp_handler(req: Request, exc: RequestValidationError):
    if "/login" in req.url.path:
        return JSONResponse(
            status_code=INVALID_CREDENTIAL.status_code,
            content={"detail": INVALID_CREDENTIAL.detail}
        )
    
    errors = exc.errors()
    for err in errors:
        err.pop("input", None)
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
        content={"detail": errors}
    )

app.include_router(process_map.router, prefix="/api/map")
app.include_router(events.router, prefix="/api/events")
app.include_router(users.router, prefix="/api/users")