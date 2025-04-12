from fastapi import APIRouter
from fastapi.staticfiles import StaticFiles

frontend_router = APIRouter()

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


# Mount frontend HTML and tile assets
frontend_router.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")
frontend_router.mount("/tiles", StaticFiles(directory="frontend/tiles"), name="tiles")
