from fastapi import APIRouter
from fastapi.staticfiles import StaticFiles

frontend_router = APIRouter()

# Mount frontend HTML and tile assets
frontend_router.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")
frontend_router.mount("/tiles", StaticFiles(directory="frontend/tiles"), name="tiles")
