# utils/db_utils.py
from sqlalchemy.orm import Session
from models.game_state_db import GameStateDB
from game_logic.data.game_state import GameState, asdict

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
