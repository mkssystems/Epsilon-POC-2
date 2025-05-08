# game_logic/validation/sync_validator.py
from sqlalchemy.orm import Session
from game_logic.data.game_state import GameState
from utils.db_utils import retrieve_game_state_from_db

def validate_sync(session_id: str, client_turn: int, client_phase: str, db_session: Session):
    """
    Explicitly validate synchronization between mobile and backend states.
    Args:
        session_id: Explicit session ID of the game.
        client_turn: Turn number explicitly reported by mobile client.
        client_phase: Game phase explicitly reported by mobile client.
        db_session: Explicitly passed DB session for querying.

    Returns:
        dict: Explicit validation result with sync status and details.
    """
    # Retrieve authoritative game state explicitly from backend
    game_state: GameState = retrieve_game_state_from_db(db_session, session_id)

    if not game_state:
        return {"status": "error", "detail": "Game state not found."}

    backend_turn = game_state.turn.number
    backend_phase = game_state.phase.name.value

    # Explicit check for state synchronization
    if client_turn == backend_turn and client_phase == backend_phase:
        return {"status": "ok"}
    
    # Explicit mismatch details for debugging and mobile resync
    return {
        "status": "mismatch",
        "backend_turn": backend_turn,
        "backend_phase": backend_phase,
        "client_turn": client_turn,
        "client_phase": client_phase
    }
