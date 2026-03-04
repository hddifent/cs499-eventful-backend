from fastapi import FastAPI
from app.api import process_map, events, users

app = FastAPI()

app.include_router(process_map.router, prefix="/api/map")
app.include_router(events.router, prefix="/api/events")
app.include_router(users.router, prefix="/api/users")