# game_logic/phases/turn_zero.py
from datetime import datetime
from game_logic.data.game_state import GamePhaseName, TurnInfo, PhaseInfo, Entity, GameState
from utils.db_utils import save_game_state_to_db

def execute_turn_zero(db_session, game_state: GameState):
    current_time = datetime.utcnow()

    # Explicitly initialize TurnInfo
    game_state.turn = TurnInfo(
        number=0,
        started_at=current_time
    )

    # Explicitly initialize PhaseInfo
    game_state.phase = PhaseInfo(
        name=GamePhaseName.TURN_0,
        number=None,
        is_end_turn=False,
        started_at=current_time
    )

    # Explicitly mocked minimal initial entities
    game_state.entities = [
        Entity(id="entity_player_1", type="player", position="start_tile", controlled_by_user_id="user_1"),
        Entity(id="entity_npc_1", type="npc", position="npc_start_tile")
    ]

    # Explicitly mocked minimal labyrinth structure
    game_state.labyrinth = {
        "tiles": {
            "start_tile": {"type": "start", "connected_tiles": ["tile_1"]},
            "npc_start_tile": {"type": "npc_start", "connected_tiles": ["tile_2"]}
        },
        "layout": "mocked_layout"
    }

    # Explicitly save initial Turn 0 game state to DB
    save_game_state_to_db(db_session, game_state)

    print(f"[INFO] Turn 0 explicitly initialized and saved for session {game_state.session_id}")
