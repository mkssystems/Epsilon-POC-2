from sqlalchemy.orm import Session
from game_logic.models.game_state_db import GameStateDB
from game_logic.data.game_state import GameState, asdict
from config import SessionLocal
import json
from datetime import datetime
from enum import Enum  # Explicitly import Enum class

# Explicit helper function to convert datetime and enum to string
def json_serializer(obj):
    if isinstance(obj, datetime):
        return obj.isoformat()
    if isinstance(obj, Enum):
        return obj.value  # Explicitly serialize enums by their value
    raise TypeError(f"Type {type(obj)} not serializable")

def save_game_state_to_db(session: Session, game_state: GameState):
    session_id = game_state.session_id
    db_entry = session.query(GameStateDB).filter_by(session_id=session_id).first()

    if db_entry:
        db_entry.game_state = {}  # Temporarily minimal mock (avoid serialization)
    else:
        db_entry = GameStateDB(session_id=session_id, game_state={})
        session.add(db_entry)

    session.commit()
    print("[DEBUG] Minimal game state saved for testing")


def get_db_session() -> Session:
    return SessionLocal()

def load_initial_game_state(session: Session, session_id: str) -> GameState:
    db_entry = session.query(GameStateDB).filter_by(session_id=session_id).first()

    if db_entry:
        game_state_dict = db_entry.game_state
        game_state = GameState(**game_state_dict)
    else:
        game_state = GameState(
            session_id=session_id,
            turn=None,
            phase=None,
            entities=[],
            labyrinth={}
        )
        new_db_entry = GameStateDB(
            session_id=session_id,
            game_state=json.loads(json.dumps(asdict(game_state), default=json_serializer))
        )
        session.add(new_db_entry)
        session.commit()
        print(f"[INFO] Explicitly initialized new game state entry for session_id={session_id}")

    return game_state
