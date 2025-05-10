# game_logic/validation/sync_validator.py

from sqlalchemy.orm import Session
from utils.db_utils import load_initial_game_state

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
    # Retrieve authoritative game state explicitly from backend as a dictionary
    game_state_dict = load_initial_game_state(db_session, session_id)

    if not game_state_dict:
        return {"status": "error", "detail": "Game state not found."}

    try:
        # Explicit dictionary key access instead of attribute access
        backend_turn = game_state_dict['turn']['number']
        backend_phase = game_state_dict['phase']['name']
    except KeyError as e:
        # Explicitly handle missing keys
        return {
            "status": "error",
            "detail": f"Malformed game state explicitly detected: missing key {e}"
        }

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
