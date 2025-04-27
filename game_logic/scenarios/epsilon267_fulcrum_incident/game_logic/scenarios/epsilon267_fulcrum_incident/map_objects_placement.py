# game_logic/scenarios/epsilon267_fulcrum_incident/map_objects_placement.py
import random
from models.tile import Tile
from models.map_object import MapObject

# Explicitly place map objects randomly (allowing placement on tiles with entities)
def place_map_objects(db_session, labyrinth_id, scenario_name):
    tile_records = db_session.query(Tile).filter(Tile.labyrinth_id == labyrinth_id).all()

    map_objects = db_session.query(MapObject).filter(MapObject.scenario == scenario_name).all()

    if not tile_records:
        raise ValueError("No available tiles to place map objects explicitly")

    map_object_positions = {}
    for map_object in map_objects:
        tile = random.choice(tile_records)
        map_object_positions[str(map_object.id)] = {
            "name": map_object.name,
            "description": map_object.description,
            "position": str(tile.id)
        }

    return map_object_positions
