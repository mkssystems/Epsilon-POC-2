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

import os

# FastAPI app initialization
app = FastAPI()

# SQLAlchemy database setup
DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

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
    Base.metadata.create_all(bind=engine)

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

class LabyrinthResponse(BaseModel):
    seed: str
    start_x: int
    start_y: int
    tiles: List[LabyrinthTile]

# Endpoint to list game sessions
@app.get("/game-sessions", response_model=List[GameSessionResponse])
def list_game_sessions(db: Session = Depends(get_db)):
    return db.query(GameSession).all()

# Endpoint to create a new game session
@app.post("/create-game-session", response_model=GameSessionResponse)
def create_game_session(request: GameSessionCreateRequest, db: Session = Depends(get_db)):
    labyrinth = generate_labyrinth(size=request.size, seed=request.seed, db=db)

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
    labyrinth = generate_labyrinth(size=request.size, seed=request.seed, db=db)

    tiles_data = [
        LabyrinthTile(
            x=tile.x,
            y=tile.y,
            type=tile.type,
            open_directions=list(tile.open_directions)
        )
        for tile in db.query(Tile).filter(Tile.labyrinth_id == labyrinth.id).all()
    ]

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
