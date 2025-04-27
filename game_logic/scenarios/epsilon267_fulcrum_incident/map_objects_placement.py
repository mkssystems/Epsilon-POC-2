# game_logic/scenarios/epsilon267_fulcrum_incident/map_objects_placement.py
import random
from models.tile import Tile
from models.game_session import GameSession
from models.map_object import MapObject

# Helper function to explicitly retrieve labyrinth tiles by session ID
def get_labyrinth_tiles(db_session, session_id):
    session_record = db_session.query(GameSession).filter(GameSession.id == session_id).first()
    if not session_record:
        raise ValueError(f"[ERROR] GameSession not found for session_id={session_id}")

    tiles = db_session.query(Tile).filter(Tile.labyrinth_id == session_record.labyrinth_id).all()

    if not tiles:
        raise ValueError(f"[ERROR] No tiles found for labyrinth_id={session_record.labyrinth_id}")

    return tiles

# Explicitly place map objects randomly (allowing placement on tiles with entities)
def place_map_objects(db_session, session_id, scenario_name):
    # Retrieve tiles correctly linked to the session's labyrinth
    tile_records = get_labyrinth_tiles(db_session, session_id)

    # Fetch map objects related to the current scenario
    map_objects = db_session.query(MapObject).filter(MapObject.scenario == scenario_name).all()

    if not tile_records:
        raise ValueError("[ERROR] No available tiles to place map objects explicitly")

    if not map_objects:
        raise ValueError(f"[ERROR] No map objects found for scenario '{scenario_name}'")

    # Assign each map object randomly to a tile
    map_object_positions = {}
    for map_object in map_objects:
        tile = random.choice(tile_records)
        map_object_positions[str(map_object.id)] = {
            "name": map_object.name,
            "description": map_object.description,
            "position": str(tile.id)
        }

    return map_object_positions

