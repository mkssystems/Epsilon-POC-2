# game_logic/scenarios/epsilon267_fulcrum_incident/epsilon267_fulcrum_incident_entities_placement.py
import random
from models.tile import Tile
from models.game_entities import Entity as DbEntity

# Helper function to calculate distances (Manhattan distance for simplicity)
def tile_distance(tile_a, tile_b):
    return abs(tile_a.x - tile_b.x) + abs(tile_a.y - tile_b.y)

# Explicitly place all players on one random tile
def place_players(db_session, labyrinth_id, entity_records):
    tile_records = db_session.query(Tile).filter(Tile.labyrinth_id == labyrinth_id).all()
    starting_tile = random.choice(tile_records)

    player_positions = {}
    for entity_record in entity_records:
        player_positions[entity_record.id] = str(starting_tile.id)

    return player_positions, starting_tile

# Explicitly place boss enemy at least 2 tiles away from players
def place_enemies(db_session, labyrinth_id, enemy_records, player_tile):
    tile_records = db_session.query(Tile).filter(Tile.labyrinth_id == labyrinth_id).all()

    boss_tile_candidates = [tile for tile in tile_records if tile_distance(tile, player_tile) >= 2]
    boss_tile = random.choice(boss_tile_candidates)

    enemy_positions = {}
    for enemy in enemy_records:
        if enemy.role == "Boss Unit":
            enemy_positions[enemy.id] = str(boss_tile.id)
        else:
            available_tiles = [tile for tile in tile_records if tile.id != boss_tile.id and tile.id != player_tile.id]
            enemy_tile = random.choice(available_tiles)
            enemy_positions[enemy.id] = str(enemy_tile.id)

    return enemy_positions, boss_tile

# Explicitly place NPC as far as possible from boss
def place_npcs(db_session, labyrinth_id, npc_records, boss_tile):
    tile_records = db_session.query(Tile).filter(Tile.labyrinth_id == labyrinth_id).all()
    npc_tile = max(tile_records, key=lambda tile: tile_distance(tile, boss_tile))

    npc_positions = {npc.id: str(npc_tile.id) for npc in npc_records}

    return npc_positions
