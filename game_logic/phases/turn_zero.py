# game_logic/phases/turn_zero.py
from datetime import datetime
from game_logic.data.game_state import GamePhaseName, TurnInfo, PhaseInfo, Entity, GameState
from utils.db_utils import save_game_state_to_db
from realtime import broadcast_session_update
import asyncio
from models.game_session import GameSession
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

# Placeholder for initializing turn information
def initialize_turn_info(game_state):
    pass

# Placeholder for initializing phase information
def initialize_phase_info(game_state):
    pass

# Placeholder for defining initial entities
def define_initial_entities(game_state):
    pass

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

# Placeholder for saving initialized state
def save_initialized_state(db_session, game_state):
    pass

# Main procedural orchestrating function for Turn 0 initialization
def execute_turn_zero(db_session, game_state: GameState):
    # Retrieve scenario name explicitly
    scenario_name = retrieve_scenario_name(db_session, game_state.session_id)

    # Explicitly broadcast the scenario start event
    broadcast_game_started(game_state.session_id, scenario_name)

    print(f"[INFO] Turn 0 explicitly started with scenario '{scenario_name}' for session {game_state.session_id}")
