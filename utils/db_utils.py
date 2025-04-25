# utils/db_utils.py

from sqlalchemy.orm import Session
from game_logic.models.game_state_db import GameStateDB
from game_logic.data.game_state import GameState, asdict
from config import SessionLocal


# Function explicitly saving/updating GameState to database
def save_game_state_to_db(session: Session, game_state: GameState):
    state_dict = asdict(game_state)  # Explicit conversion to dict suitable for JSON serialization
    session_id = game_state.session_id

    # Retrieve existing entry explicitly by session_id
    db_entry = session.query(GameStateDB).get(session_id)

    if db_entry:
        # Update explicitly if entry already exists
        db_entry.game_state = state_dict
    else:
        # Create explicitly a new DB entry if not existing
        db_entry = GameStateDB(session_id=session_id, game_state=state_dict)
        session.add(db_entry)

    session.commit()  # Explicitly persist changes to the database

# Explicitly returns a new active database session
def get_db_session() -> Session:
    return SessionLocal()

# Explicitly loads existing GameState or creates a new one if not found
def load_initial_game_state(session: Session, session_id: str) -> GameState:
    # Retrieve existing entry explicitly by session_id
    db_entry = session.query(GameStateDB).get(session_id)

    if db_entry:
        # Explicitly reconstruct GameState from stored dict
        game_state_dict = db_entry.game_state
        game_state = GameState(**game_state_dict)
    else:
        # Explicitly create new GameState if it doesn't exist
        game_state = GameState(session_id=session_id, phase=None, turn_number=0)
        new_db_entry = GameStateDB(session_id=session_id, game_state=asdict(game_state))
        session.add(new_db_entry)
        session.commit()

    return game_state
