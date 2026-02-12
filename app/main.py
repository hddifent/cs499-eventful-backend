from fastapi import FastAPI
from app.api import process_map, events

from dotenv import load_dotenv 

load_dotenv()

app = FastAPI()

app.include_router(process_map.router, prefix="/api/map")
app.include_router(events.router, prefix="/api/events")