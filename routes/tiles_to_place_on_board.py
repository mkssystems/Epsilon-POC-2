# routes/tiles_to_place_on_board.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID
from db.session import get_db
from models.tile import Tile
from models.game_session import GameSession

router = APIRouter()

@router.get("/game-state/{session_id}/tiles-to-place")
async def get_tiles_to_place(session_id: UUID, db: Session = Depends(get_db)):
    # Explicitly fetch the labyrinth_id for the current game session
    game_session = db.query(GameSession).filter(GameSession.id == session_id).first()

    if not game_session:
        raise HTTPException(status_code=404, detail="Game session explicitly not found.")

    labyrinth_id = game_session.labyrinth_id

    # Explicitly fetch tiles that are revealed but not yet on the board
    tiles_to_place = db.query(Tile).filter(
        Tile.labyrinth_id == labyrinth_id,
        Tile.revealed == True,
        Tile.on_board == False
    ).all()

    # Explicitly format the response clearly
    response = [
        {
            "id": str(tile.id),
            "x": tile.x,
            "y": tile.y,
            "type": tile.type,
            "tile_code": tile.tile_code,
            "open_directions": tile.open_directions,
            "thematic_area": tile.thematic_area
        }
        for tile in tiles_to_place
    ]

    return {"tiles_to_place": response}
