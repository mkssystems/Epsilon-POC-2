from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from utils.corrected_labyrinth_backend_seed_fixed import generate_labyrinth  # Import labyrinth generator
from models.game_session import GameSession
from models.player import Player
from models.labyrinth import Labyrinth  # Import the Labyrinth model
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from typing import List
from fastapi import Depends
from sqlalchemy.orm import Session
from models.game_session import GameSession  # ensure correct import
from pydantic import BaseModel
from datetime import datetime

@app.on_event("startup")
def startup():
    # Initialize database tables
    Base.metadata.create_all(bind=engine)

# FastAPI app initialization
app = FastAPI()

# SQLAlchemy database setup
DATABASE_URL = "postgresql://username:password@localhost:5432/your_database"  # Update with your database URL
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

# Pydantic model for request data
class GameSessionCreateRequest(BaseModel):
    size: int
    seed: str

# Dependency to get the database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class GameSessionResponse(BaseModel):
    id: str
    seed: str
    labyrinth_id: str
    start_x: int
    start_y: int
    created_at: datetime

    class Config:
        orm_mode = True

@app.get("/game-sessions", response_model=List[GameSessionResponse])
def list_game_sessions(db: Session = Depends(get_db)):
    sessions = db.query(GameSession).all()
    return sessions

@app.post("/create-game-session")
def create_game_session(request: GameSessionCreateRequest, db: Session = Depends(get_db)):
    # Generate the labyrinth using the function from corrected_labyrinth_backend_seed_fixed.py
    labyrinth = generate_labyrinth(size=request.size, seed=request.seed, db=db)
    
    # Create a new game session based on the generated labyrinth
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
