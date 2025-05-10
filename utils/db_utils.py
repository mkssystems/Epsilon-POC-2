# utils/db_utils.py

from sqlalchemy.orm import Session
from game_logic.models.game_state_db import GameStateDB
from game_logic.data.game_state import GameState, GameInfo, TurnInfo, PhaseInfo, GamePhaseName, asdict
from config import SessionLocal
import json
from datetime import datetime
from enum import Enum
from utils.game_state_logger import log_game_state  # Explicitly import logging utility

# Explicit helper function to convert datetime and enum to string
def json_serializer(obj):
    if isinstance(obj, datetime):
        return obj.isoformat()
    if isinstance(obj, Enum):
        return obj.value
    raise TypeError(f"Type {type(obj)} not serializable")

# Explicitly saves game state to the database and logs it for debugging
def save_game_state_to_db(session: Session, game_state: GameState):
    state_dict = asdict(game_state)
    session_id = game_state.game_info.session_id

    db_entry = session.query(GameStateDB).filter_by(session_id=session_id).first()

    if db_entry:
        db_entry.game_state = json.loads(json.dumps(state_dict, default=json_serializer))
    else:
        db_entry = GameStateDB(
            session_id=session_id,
            game_state=json.loads(json.dumps(state_dict, default=json_serializer))
        )
        session.add(db_entry)

    try:
        session.commit()
        print(f"[INFO] Game state explicitly saved successfully for session_id={session_id}")

        # Explicitly log the saved game state
        log_game_state(session_id, state_dict)

    except Exception as e:
        session.rollback()
        print(f"[ERROR] Failed to explicitly save game state: {e}")

# Explicitly returns a new database session
def get_db_session() -> Session:
    return SessionLocal()

# Explicitly loads initial game state from database, or initializes if none exists
def load_initial_game_state(session: Session, session_id: str) -> GameState:
    db_entry = session.query(GameStateDB).filter_by(session_id=session_id).first()

    if db_entry:
        game_state_dict = db_entry.game_state
        game_state = GameState(**game_state_dict)
    else:
        # Explicitly initialize a default game state structure
        game_info = GameInfo(
            session_id=session_id,
            scenario="Unknown",
            labyrinth_id="",
            size=0,
            seed=""
        )

        turn_info = TurnInfo(
            number=0,
            started_at=datetime.utcnow()
        )

        phase_info = PhaseInfo(
            name=GamePhaseName.TURN_0,
            number=None,
            is_end_turn=False,
            started_at=datetime.utcnow()
        )

        game_state = GameState(
            game_info=game_info,
            turn=turn_info,
            phase=phase_info,
            entities={},
            labyrinth={}
        )

        new_db_entry = GameStateDB(
            session_id=session_id,
            game_state=json.loads(json.dumps(asdict(game_state), default=json_serializer))
        )
        session.add(new_db_entry)
        session.commit()
        print(f"[INFO] Explicitly initialized new game state entry for session_id={session_id}")

        # Explicitly log the initialized game state
        log_game_state(session_id, asdict(game_state))

    return game_state
