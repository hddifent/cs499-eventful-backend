from fastapi import FastAPI
from app.api import process_map

app = FastAPI()

app.include_router(process_map.router, prefix="/api/map")
