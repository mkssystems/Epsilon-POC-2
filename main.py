# main.py

from fastapi import FastAPI, Depends
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session, sessionmaker
from pydantic import BaseModel
from typing import List, Optional, Dict
from datetime import datetime
from sqlalchemy import text
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
from models import Base as EntityBase
from db.init_data import load_data
from db.session import get_db

from models.game_entities import Entity
from models.equipment import Equipment
from models.skills import Skill
from models.specials import Special
from state import session_readiness, lock

from config import DATABASE_URL

# Import API router
from routes.api import router as api_router

# Import for real-time socket
from realtime import mount_websocket_routes, broadcast_session_update

app = FastAPI()

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

FORCE_REINIT_DB = True

@app.on_event("startup")
def startup():
    def init_db():
        if FORCE_REINIT_DB:
            print("⚠️ Reinitializing the database from scratch...")

            # Safely attempt to drop existing tables
            try:
                EntityBase.metadata.drop_all(bind=engine)
                print("✅ Tables dropped successfully.")
            except Exception as e:
                print(f"⚠️ Warning during drop_all: {e}")

            # Safely recreate all tables
            try:
                EntityBase.metadata.create_all(bind=engine)
                print("✅ Tables created successfully.")
            except Exception as e:
                print(f"❌ Error during create_all: {e}")
                return  # Exit initialization if create fails

            # Load initial seed data
            try:
                df_entities = pd.read_csv("assets/seed/entities.csv")
                df_equipment = pd.read_csv("assets/seed/equipment.csv")
                df_skills = pd.read_csv("assets/seed/skills.csv")
                df_specials = pd.read_csv("assets/seed/specials.csv")
                df_map_object = pd.read_csv("assets/seed/map_objects.csv")

                load_data(engine, df_entities, df_equipment, df_skills, df_specials, df_map_object)
                print("✅ Seed data loaded successfully.")
            except Exception as e:
                print(f"❌ Error during seed data loading: {e}")
                return

            print("🚀 Database initialization complete and successful.")

    # Start initialization asynchronously
    threading.Thread(target=init_db).start()




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

def parse_directions(open_directions):
    if isinstance(open_directions, str):
        try:
            return json.loads(open_directions)
        except:
            return [open_directions]
    return open_directions

def get_image_name(tile_type, directions):
    directions = sorted(directions)
    if tile_type == "crossroad":
        return "tile_crossroad.png"
    elif tile_type == "corridor":
        return "tile_corridor_NS.png" if directions == ["N", "S"] else "tile_corridor_EW.png"
    elif tile_type == "turn":
        if directions == ["E", "N"]: return "tile_turn_NE.png"
        elif directions == ["N", "W"]: return "tile_turn_NW.png"
        elif directions == ["E", "S"]: return "tile_turn_SE.png"
        elif directions == ["S", "W"]: return "tile_turn_SW.png"
    elif tile_type == "t_section":
        missing_direction = ({"N", "E", "S", "W"} - set(directions)).pop()
        return f"tile_t_section_{missing_direction}.png"
    elif tile_type == "dead_end":
        return f"tile_dead_end_{directions[0]}.png"
    return "tile_crossroad.png"

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
        image_name = get_image_name(tile_db.type, directions)

        tile = LabyrinthTile(
            x=tile_db.x,
            y=tile_db.y,
            type=tile_db.type,
            open_directions=directions,
            image=image_name
        )
        tiles_data.append(tile)

    return LabyrinthResponse(
        seed=labyrinth.seed,
        start_x=labyrinth.start_x,
        start_y=labyrinth.start_y,
        tiles=tiles_data
    )

@app.delete("/destroy-all-sessions")
def destroy_all_sessions(db: Session = Depends(get_db)):
    db.query(GameSession).delete()
    db.commit()
    return {"detail": "All game sessions deleted"}

# WebSocket endpoint registration FIRST
mount_websocket_routes(app)

# Include API router SECOND
app.include_router(api_router)

# Mount static files LAST
app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")
app.mount("/tiles", StaticFiles(directory="frontend/tiles"), name="tiles")
