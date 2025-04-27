# game_logic/phases/turn_zero.py
from datetime import datetime
from game_logic.data.game_state import GamePhaseName, TurnInfo, PhaseInfo, Entity, GameState
from utils.db_utils import save_game_state_to_db
from realtime import broadcast_session_update
import asyncio
from models.game_session import GameSession
from game_logic.scenarios.epsilon267_fulcrum_incident.epsilon267_fulcrum_incident_entities_placement import (
    place_players,
    place_enemies,
    place_npcs
)
from game_logic.scenarios.epsilon267_fulcrum_incident.map_objects_placement import place_map_objects
from models.game_entities import Entity as DbEntity
from models.tile import Tile

# Explicitly retrieve scenario name from the database
def retrieve_scenario_name(db_session, session_id):
    session_record = db_session.query(GameSession).filter(GameSession.id == session_id).first()
    return session_record.scenario_name if session_record else "Unknown Scenario"

# Explicitly broadcast game start event asynchronously
def broadcast_game_started(session_id, scenario_name):
    message = {
        "event": "game_started",
        "scenario_name": scenario_name
    }
    asyncio.create_task(broadcast_session_update(session_id, message))

# Explicitly initialize turn information
def initialize_turn_info(game_state):
    game_state.turn = TurnInfo(number=0, started_at=datetime.utcnow())

# Explicitly initialize phase information
def initialize_phase_info(game_state):
    game_state.phase = PhaseInfo(
        name=GamePhaseName.TURN_0,
        number=None,
        is_end_turn=False,
        started_at=datetime.utcnow()
    )

# Explicitly define initial labyrinth layout by loading tiles and setting their initial revealed status to False
def define_initial_labyrinth(db_session, game_state):
    tile_records = db_session.query(Tile).filter(Tile.labyrinth_id == game_state.session_id).all()

    labyrinth_layout = {}
    for tile in tile_records:
        labyrinth_layout[str(tile.id)] = {
            "x": tile.x,
            "y": tile.y,
            "type": tile.type,
            "open_directions": tile.open_directions,
            "revealed": False
        }

    game_state.labyrinth = labyrinth_layout

    print(f"[INFO] Labyrinth explicitly initialized with {len(tile_records)} tiles for session {game_state.session_id}")

# Explicitly define initial placement using scenario-specific logic
def define_initial_placement(db_session, game_state):
    scenario_name = retrieve_scenario_name(db_session, game_state.session_id)

    if scenario_name == "Epsilon267-Fulcrum Incident":
        player_entities = db_session.query(DbEntity).filter(DbEntity.scenario == scenario_name, DbEntity.type == "player").all()
        enemy_entities = db_session.query(DbEntity).filter(DbEntity.scenario == scenario_name, DbEntity.type == "enemy").all()
        npc_entities = db_session.query(DbEntity).filter(DbEntity.scenario == scenario_name, DbEntity.type == "npc").all()

        player_positions, player_tile = place_players(db_session, game_state.session_id, player_entities)
        enemy_positions, boss_tile = place_enemies(db_session, game_state.session_id, enemy_entities, player_tile)
        npc_positions = place_npcs(db_session, game_state.session_id, npc_entities, boss_tile)

        all_positions = {**player_positions, **enemy_positions, **npc_positions}
        game_state.entities = all_positions

        map_object_positions = place_map_objects(db_session, game_state.session_id, scenario_name)
        game_state.map_objects = map_object_positions

        print(f"[INFO] Entities and map objects explicitly positioned using scenario-specific logic for '{scenario_name}'")
    else:
        print(f"[WARN] Scenario '{scenario_name}' not explicitly handled for entity and map object placement.")

# Explicitly save initialized state to the database
def save_initialized_state(db_session, game_state):
    try:
        save_game_state_to_db(db_session, game_state)
        print(f"[INFO] Initialized game state explicitly saved for session {game_state.session_id}")
    except Exception as e:
        print(f"[ERROR] Failed to explicitly save initialized game state for session {game_state.session_id}: {e}")
        raise

# Main procedural orchestrating function for Turn 0 initialization
def execute_turn_zero(db_session, game_state: GameState):
    scenario_name = retrieve_scenario_name(db_session, game_state.session_id)
    broadcast_game_started(game_state.session_id, scenario_name)

    initialize_turn_info(game_state)
    initialize_phase_info(game_state)
    define_initial_labyrinth(db_session, game_state)
    define_initial_placement(db_session, game_state)
    save_initialized_state(db_session, game_state)

    print(f"[INFO] Turn 0 explicitly started with scenario '{scenario_name}' for session {game_state.session_id}")
