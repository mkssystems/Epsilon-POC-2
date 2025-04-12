from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from models.game_session import GameSession
from models.tile import Tile
from utils.corrected_labyrinth_backend_seed_fixed import generate_labyrinth
from db.session import get_db
from typing import List, Optional
from pydantic import BaseModel
import json

frontend_router = APIRouter()

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

@frontend_router.delete("/destroy-all-sessions")
def destroy_all_sessions(db: Session = Depends(get_db)):
    db.query(GameSession).delete()
    db.commit()
    return {"detail": "All game sessions deleted"}

@frontend_router.post("/generate-labyrinth", response_model=LabyrinthResponse)
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

def get_image_name(tile_type, directions):
    directions = sorted(directions)
    # Tile image mapping logic...
    if tile_type == "crossroad":
        return "tile_crossroad.png"
    # ... (rest unchanged)

def parse_directions(open_directions):
    if isinstance(open_directions, str):
        try:
            return json.loads(open_directions)
        except:
            return [open_directions]
    return open_directions
