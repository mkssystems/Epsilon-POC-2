# game_logic/scenarios/epsilon267_fulcrum_incident/epsilon267_fulcrum_incident_entities_placement.py
import random
from models.tile import Tile
from models.game_session import GameSession

# Helper function to calculate Manhattan distance between two tiles
def tile_distance(tile_a, tile_b):
    return abs(tile_a.x - tile_b.x) + abs(tile_a.y - tile_b.y)

# Retrieve tiles explicitly by the correct labyrinth ID from game session
def get_labyrinth_tiles(db_session, session_id):
    session_record = db_session.query(GameSession).filter(GameSession.id == session_id).first()
    if not session_record:
        raise ValueError(f"[ERROR] GameSession not found for session_id={session_id}")

    tiles = db_session.query(Tile).filter(Tile.labyrinth_id == session_record.labyrinth_id).all()

    if not tiles:
        raise ValueError(f"[ERROR] No tiles found for labyrinth_id={session_record.labyrinth_id}")

    return tiles

# Explicitly place all player entities on one randomly selected starting tile
def place_players(db_session, session_id, entity_records):
    tile_records = get_labyrinth_tiles(db_session, session_id)
    starting_tile = random.choice(tile_records)

    player_positions = {entity_record.id: str(starting_tile.id) for entity_record in entity_records}

    return player_positions, starting_tile

# Explicitly place enemies, ensuring boss enemy is placed at least 2 tiles away from players
def place_enemies(db_session, session_id, enemy_records, player_tile):
    tile_records = get_labyrinth_tiles(db_session, session_id)

    boss_tile_candidates = [tile for tile in tile_records if tile_distance(tile, player_tile) >= 2]

    if not boss_tile_candidates:
        raise ValueError("[ERROR] No suitable tile found for boss placement at minimum distance from players.")

    boss_tile = random.choice(boss_tile_candidates)

    enemy_positions = {}
    for enemy in enemy_records:
        if enemy.role == "Boss Unit":
            enemy_positions[enemy.id] = str(boss_tile.id)
        else:
            available_tiles = [
                tile for tile in tile_records
                if tile.id not in [boss_tile.id, player_tile.id]
            ]
            if not available_tiles:
                raise ValueError("[ERROR] No available tiles left to place additional enemies.")
            enemy_tile = random.choice(available_tiles)
            enemy_positions[enemy.id] = str(enemy_tile.id)

    return enemy_positions, boss_tile

# Explicitly place NPCs at the tile furthest away from boss enemy
def place_npcs(db_session, session_id, npc_records, boss_tile):
    tile_records = get_labyrinth_tiles(db_session, session_id)

    npc_tile = max(tile_records, key=lambda tile: tile_distance(tile, boss_tile))

    npc_positions = {npc.id: str(npc_tile.id) for npc in npc_records}

    return npc_positions
