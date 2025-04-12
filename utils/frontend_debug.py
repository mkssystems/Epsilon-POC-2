from fastapi import APIRouter, Depends
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from uuid import UUID
import json

from models.game_session import GameSession
from models.tile import Tile
from utils.corrected_labyrinth_backend_seed_fixed import generate_labyrinth
from db.session import get_db

frontend_router = APIRouter()

# ===== Pydantic models used for labyrinth visualization =====
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

# ====== Debug-only endpoint: destroy all sessions ======
@frontend_router.delete("/destroy-all-sessions")
def destroy_all_sessions(db: Session = Depends(get_db)):
    db.query(GameSession).delete()
    db.commit()
    return {"detail": "All game sessions deleted"}

# ====== Labyrinth visualization ======
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

# ====== Tile-to-image mapping ======
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

# ====== Convert JSON direction strings to list ======
def parse_directions(open_directions):
    if isinstance(open_directions, str):
        try:
            return json.loads(open_directions)
        except:
            return [open_directions]
    return open_directions

# ====== Static file mounts for HTML frontend and tiles ======
frontend_router.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")
frontend_router.mount("/tiles", StaticFiles(directory="frontend/tiles"), name="tiles")
