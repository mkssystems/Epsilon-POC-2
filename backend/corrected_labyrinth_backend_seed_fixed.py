
from fastapi import FastAPI, APIRouter, HTTPException, Depends
from fastapi.staticfiles import StaticFiles
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, JSON, Boolean, DateTime
from sqlalchemy.orm import sessionmaker, relationship, declarative_base, Session
from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import List, Optional
import random
import uuid
import os

app = FastAPI()
router = APIRouter()

DATABASE_URL = "postgresql://epsilon_51hw_user:odXXC7QP1IpBhOQTAjdBs5uksmiufu6H@dpg-cvmm76vfte5s738rpks0-a/epsilon_51hw"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

class Labyrinth(Base):
    __tablename__ = "labyrinths"
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    size = Column(Integer)
    seed = Column(String(100), nullable=True)
    start_x = Column(Integer)
    start_y = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)

    tiles = relationship("Tile", back_populates="labyrinth")

class Tile(Base):
    __tablename__ = "tiles"
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    labyrinth_id = Column(String(36), ForeignKey("labyrinths.id"))
    x = Column(Integer)
    y = Column(Integer)
    type = Column(String(20))
    open_directions = Column(JSON)
    revealed = Column(Boolean, default=False)

    labyrinth = relationship("Labyrinth", back_populates="tiles")

class TileSchema(BaseModel):
    x: int
    y: int
    type: str
    open_directions: List[str]
    model_config = ConfigDict(from_attributes=True)

class LabyrinthCreateRequest(BaseModel):
    size: int
    seed: Optional[str] = None

class LabyrinthResponse(BaseModel):
    id: str
    size: int
    seed: Optional[str]
    start_x: int
    start_y: int
    tiles: List[TileSchema]
    model_config = ConfigDict(from_attributes=True)

DIRECTIONS = {"N": (0, -1), "S": (0, 1), "E": (1, 0), "W": (-1, 0)}
OPPOSITE = {"N": "S", "S": "N", "E": "W", "W": "E"}

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_tile_type_from_directions(directions):
    sorted_dirs = sorted(directions)
    if len(directions) == 1:
        return "dead_end"
    elif len(directions) == 2:
        if ("N" in directions and "S" in directions) or ("E" in directions and "W" in directions):
            return "corridor"
        else:
            return "turn"
    elif len(directions) == 3:
        return "t_section"
    else:
        return "crossroad"

def generate_labyrinth(size: int, seed: Optional[str], db: Session) -> Labyrinth:
    if size < 4 or size > 10:
        raise ValueError("Size must be between 4 and 10")

    if not seed:
        seed = uuid.uuid4().hex
    random.seed(seed)

    labyrinth = Labyrinth(size=size, seed=seed)
    db.add(labyrinth)
    db.commit()
    db.refresh(labyrinth)

    visited = [[False] * size for _ in range(size)]
    tile_map = {}

    def dfs(x, y):
        visited[y][x] = True
        directions = list(DIRECTIONS.keys())
        random.shuffle(directions)
        current_open = []

        for direction in directions:
            nx, ny = x + DIRECTIONS[direction][0], y + DIRECTIONS[direction][1]
            if 0 <= nx < size and 0 <= ny < size and not visited[ny][nx]:
                current_open.append(direction)
                dfs(nx, ny)
                neighbor_tile = tile_map[(nx, ny)]
                neighbor_tile['open_directions'].append(OPPOSITE[direction])

        tile_map[(x, y)] = {'x': x, 'y': y, 'open_directions': current_open}

    start_x, start_y = random.randint(0, size - 1), random.randint(0, size - 1)
    dfs(start_x, start_y)

    labyrinth.start_x, labyrinth.start_y = start_x, start_y

    for (x, y), tile_data in tile_map.items():
        directions = tile_data['open_directions']
        tile_type = get_tile_type_from_directions(directions)
        tile = Tile(labyrinth_id=labyrinth.id, x=x, y=y, type=tile_type, open_directions=directions)
        db.add(tile)

    db.commit()
    db.refresh(labyrinth)
    return labyrinth

@router.post("/generate-labyrinth", response_model=LabyrinthResponse)
def create_labyrinth(request: LabyrinthCreateRequest, db: Session = Depends(get_db)):
    try:
        labyrinth = generate_labyrinth(request.size, request.seed, db)
        return labyrinth
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

app.include_router(router)
frontend_path = os.path.join(os.path.dirname(__file__), "..", "frontend")
app.mount("/", StaticFiles(directory=frontend_path, html=True), name="frontend")
