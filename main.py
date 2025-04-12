from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session, sessionmaker
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from sqlalchemy import create_engine
from utils.corrected_labyrinth_backend_seed_fixed import generate_labyrinth
from uuid import UUID
import pandas as pd

from models.game_session import GameSession
from models.game_entities import Base as EntityBase
from db.init_data import load_data
from db.session import get_db
from config import DATABASE_URL, init_db
from realtime import mount_websocket_routes
from routes.api import router as api_router
from utils.frontend_debug import frontend_router
from fastapi.staticfiles import StaticFiles

app = FastAPI()

app.include_router(frontend_router, prefix="/debug")  # (remove duplicate!)
mount_websocket_routes(app)
app.include_router(api_router)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

FORCE_REINIT_DB = True

@app.on_event("startup")
def startup():
    init_db()

    if FORCE_REINIT_DB:
        EntityBase.metadata.drop_all(bind=engine, cascade=True)
        EntityBase.metadata.drop_all(bind=engine, cascade=True)

        df_entities = pd.read_csv("assets/seed/entities.csv")
        df_equipment = pd.read_csv("assets/seed/equipment.csv")
        df_skills = pd.read_csv("assets/seed/skills.csv")
        df_specials = pd.read_csv("assets/seed/specials.csv")

        load_data(engine, df_entities, df_equipment, df_skills, df_specials)

class GameSessionCreateRequest(BaseModel):
    size: int
    seed: Optional[str] = None

class GameSessionResponse(BaseModel):
    id: UUID
    seed: str
    labyrinth_id: UUID
    start_x: int
    start_y: int
    created_at: datetime

    class Config:
        from_attributes = True

@app.get("/game-sessions", response_model=List[GameSessionResponse])
def list_game_sessions(db: Session = Depends(get_db)):
    return db.query(GameSession).all()

@app.post("/create-game-session", response_model=GameSessionResponse)
def create_game_session(request: GameSessionCreateRequest, db: Session = Depends(get_db)):
    labyrinth, _ = generate_labyrinth(size=request.size, seed=request.seed, db=db)

    game_session = GameSession(
        seed=labyrinth.seed,
        labyrinth_id=labyrinth.id,
        start_x=labyrinth.start_x,
        start_y=labyrinth.start_y
    )
    db.add(game_session)
    db.commit()
    db.refresh(game_session)

    return game_session

# Mount frontend directly here (fix)
app.mount("/debug", StaticFiles(directory="frontend", html=True), name="frontend")
app.mount("/debug/tiles", StaticFiles(directory="frontend/tiles"), name="tiles")
