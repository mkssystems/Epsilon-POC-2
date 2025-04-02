from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session, sessionmaker, declarative_base
from pydantic import BaseModel
from typing import List
from datetime import datetime
from sqlalchemy import create_engine
from utils.corrected_labyrinth_backend_seed_fixed import generate_labyrinth
from models.game_session import GameSession
from models.labyrinth import Labyrinth
from models.player import Player
from models.base import Base  # Import shared Base

import os

# FastAPI app initialization
app = FastAPI()

# SQLAlchemy database setup
DATABASE_URL = os.getenv("DATABASE_URL")  # Use env var provided by Render
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

Base = declarative_base()

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

# Pydantic model for creating game sessions
class GameSessionCreateRequest(BaseModel):
    size: int
    seed: str

# Pydantic model for responses
class GameSessionResponse(BaseModel):
    id: str
    seed: str
    labyrinth_id: str
    start_x: int
    start_y: int
    created_at: datetime

    class Config:
        orm_mode = True

# Endpoint to list game sessions
@app.get("/game-sessions", response_model=List[GameSessionResponse])
def list_game_sessions(db: Session = Depends(get_db)):
    sessions = db.query(GameSession).all()
    return sessions

# Endpoint to create a new game session
@app.post("/create-game-session", response_model=GameSessionResponse)
def create_game_session(request: GameSessionCreateRequest, db: Session = Depends(get_db)):
    # Generate the labyrinth
    labyrinth = generate_labyrinth(size=request.size, seed=request.seed, db=db)

    # Create a new game session
    game_session = GameSession(
        seed=request.seed,
        labyrinth_id=labyrinth.id,
        start_x=labyrinth.start_x,
        start_y=labyrinth.start_y
    )
    db.add(game_session)
    db.commit()
    db.refresh(game_session)

    return game_session
