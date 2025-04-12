from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session, sessionmaker
from pydantic import BaseModel
from typing import List, Optional, Dict
from datetime import datetime
from sqlalchemy import create_engine
from utils.corrected_labyrinth_backend_seed_fixed import generate_labyrinth
from uuid import UUID
import json
import threading
import pandas as pd

from models.base import Base
from models.game_session import GameSession
from models.labyrinth import Labyrinth
from models.player import Player
from models.tile import Tile
from models.game_entities import Base as EntityBase
from db.init_data import load_data
from db.session import get_db

from models.game_entities import Entity
from models.equipment import Equipment
from models.skills import Skill
from models.specials import Special
from state import session_readiness, lock

from config import DATABASE_URL, init_db

# Import API router
from routes.api import router as api_router

# Import for real-time socket
from realtime import mount_websocket_routes, broadcast_session_update

# Import html 'frontend' debugger
from utils.frontend_debug import frontend_router

app = FastAPI()

app.include_router(frontend_router, prefix="/debug")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

FORCE_REINIT_DB = True

@app.on_event("startup")
def startup():
    init_db()

    if FORCE_REINIT_DB:
        print("⚠️ Reinitializing the database from scratch...")
        EntityBase.metadata.drop_all(bind=engine)
        EntityBase.metadata.create_all(bind=engine)

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

class GenerateLabyrinthRequest(BaseModel):
    size: int
    seed: Optional[str] = None

class LabyrinthTile(BaseModel):
    x: int
    y: int
    type: str
    open_directions: List[str]
    image: str

class LabyrinthResponse(BaseModel):
    seed: str
    start_x: int
    start_y: int
    tiles: List[LabyrinthTile]

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

# WebSocket endpoint registration FIRST
mount_websocket_routes(app)

# Include API router SECOND
app.include_router(api_router)

# Include Frontend Debug router with prefix "/debug"
app.include_router(frontend_router, prefix="/debug")
