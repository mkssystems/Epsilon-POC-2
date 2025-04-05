from sqlalchemy.orm import Session
from typing import Optional
import random
import uuid
from models.labyrinth import Labyrinth
from models.tile import Tile
import json

DIRECTIONS = {"N": (0, -1), "S": (0, 1), "E": (1, 0), "W": (-1, 0)}
OPPOSITE = {"N": "S", "S": "N", "E": "W", "W": "E"}

def get_tile_type_from_directions(directions):
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

def get_image_filename(tile_type, directions):
    if tile_type == "dead_end":
        return f"tile_dead_end_{directions[0]}.png"
    elif tile_type == "corridor":
        dirs = ''.join(sorted(directions))
        return f"tile_corridor_{dirs}.png"
    elif tile_type == "turn":
        dirs = ''.join(sorted(directions))
        return f"tile_turn_{dirs}.png"
    elif tile_type == "t_section":
        missing_dir = (set("NSEW") - set(directions)).pop()
        return f"tile_t_section_{missing_dir}.png"
    else:  # crossroad
        return "tile_crossroad.png"

def generate_labyrinth(size: int, seed: Optional[str], db: Session):
    if size < 4 or size > 10:
        raise ValueError("Size must be between 4 and 10")

    if not seed:
        seed = uuid.uuid4().hex
    random.seed(seed)

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

    labyrinth = Labyrinth(size=size, seed=seed, start_x=start_x, start_y=start_y)
    db.add(labyrinth)
    db.commit()
    db.refresh(labyrinth)

    tiles_response = []

    for (x, y), tile_data in tile_map.items():
        directions = sorted(tile_data['open_directions'])
        tile_type = get_tile_type_from_directions(directions)

        open_dirs_db = directions[0] if len(directions) == 1 else json.dumps(directions)

        tile = Tile(
            labyrinth_id=labyrinth.id,
            x=x,
            y=y,
            type=tile_type,
            open_directions=open_dirs_db
        )
        db.add(tile)

        tile_image = get_image_filename(tile_type, directions)
        tiles_response.append({
            "x": x,
            "y": y,
            "type": tile_type,
            "image": tile_image
        })

    db.commit()

    # DO NOT assign tiles_response to labyrinth ORM object
    # Return them separately instead
    return labyrinth, tiles_response
