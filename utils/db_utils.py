# utils/db_utils.py

from sqlalchemy.orm import Session
from game_logic.models.game_state_db import GameStateDB
from game_logic.data.game_state import GameState, asdict
from config import SessionLocal
import json

def save_game_state_to_db(session: Session, game_state: GameState):
    state_dict = asdict(game_state)
    session_id = game_state.session_id

    # Explicitly retrieve existing entry safely
    db_entry = session.query(GameStateDB).filter_by(session_id=session_id).first()

    if db_entry:
        db_entry.game_state = state_dict
    else:
        db_entry = GameStateDB(session_id=session_id, game_state=state_dict)
        session.add(db_entry)

    try:
        session.commit()
        print(f"[INFO] Game state explicitly saved successfully for session_id={session_id}")
    except Exception as e:
        session.rollback()
        print(f"[ERROR] Failed to explicitly save game state: {e}")

def get_db_session() -> Session:
    return SessionLocal()

def load_initial_game_state(session: Session, session_id: str) -> GameState:
    db_entry = session.query(GameStateDB).filter_by(session_id=session_id).first()

    if db_entry:
        game_state_dict = db_entry.game_state
        game_state = GameState(**game_state_dict)
    else:
        # Explicitly handle initializing TurnInfo and PhaseInfo to avoid None values issues
        game_state = GameState(
            session_id=session_id,
            turn=None,  # will be explicitly populated later
            phase=None,  # will be explicitly populated later
            entities=[],
            labyrinth={}
        )
        new_db_entry = GameStateDB(session_id=session_id, game_state=asdict(game_state))
        session.add(new_db_entry)
        session.commit()
        print(f"[INFO] Explicitly initialized new game state entry for session_id={session_id}")

    return game_state
