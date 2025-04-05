from fastapi import FastAPI, HTTPException, Depends
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session, sessionmaker
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from sqlalchemy import create_engine
from utils.corrected_labyrinth_backend_seed_fixed import generate_labyrinth
from uuid import UUID

# Explicitly import all model classes
from models.base import Base
from models.game_session import GameSession
from models.labyrinth import Labyrinth
from models.player import Player
from models.tile import Tile
from models.game_entities import Base as EntityBase
from db.init_data import load_data

from models.game_entities import Entity
from models.equipment import Equipment
from models.skills import Skill
from models.specials import Special

from config import DATABASE_URL, init_db  # Import init_db from config
import pandas as pd

# FastAPI app initialization
app = FastAPI()

# SQLAlchemy database setup
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

# Toggle for development-time DB reinit
FORCE_REINIT_DB = True  # Set to False in production

# Dependency to get the database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Initialize database tables on app startup
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

# Pydantic models
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

# Helper function (improved to handle directions correctly)
def parse_directions(open_directions):
    if isinstance(open_directions, str):
        try:
            return json.loads(open_directions)
        except:
            return [open_directions]
    return open_directions

# Endpoint to list game sessions
@app.get("/game-sessions", response_model=List[GameSessionResponse])
def list_game_sessions(db: Session = Depends(get_db)):
    return db.query(GameSession).all()

# Endpoint to create a new game session
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

# Endpoint to generate labyrinth without session creation
@app.post("/generate-labyrinth", response_model=LabyrinthResponse)
def generate_labyrinth_visual(request: GenerateLabyrinthRequest, db: Session = Depends(get_db)):
    labyrinth, tiles_response = generate_labyrinth(size=request.size, seed=request.seed, db=db)

    tiles_data = []
    for tile_info in tiles_response:
        tile_db = db.query(Tile).filter(
            Tile.labyrinth_id == labyrinth.id,
            Tile.x == tile_info["x"],
            Tile.y == tile_info["y"]
        ).first()

        directions = parse_directions(tile_db.open_directions)

        tile = LabyrinthTile(
            x=tile_db.x,
            y=tile_db.y,
            type=tile_db.type,
            open_directions=directions,
            image=tile_info["image"]
        )
        tiles_data.append(tile)

    return LabyrinthResponse(
        seed=labyrinth.seed,
        start_x=labyrinth.start_x,
        start_y=labyrinth.start_y,
        tiles=tiles_data
    )

# Endpoint to destroy all game sessions
@app.delete("/destroy-all-sessions")
def destroy_all_sessions(db: Session = Depends(get_db)):
    db.query(GameSession).delete()
    db.commit()
    return {"detail": "All game sessions deleted"}

# Serve frontend from 'frontend' directory
app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")

# Serve tiles explicitly
app.mount("/tiles", StaticFiles(directory="frontend/tiles"), name="tiles")
