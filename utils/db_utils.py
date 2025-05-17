# utils/db_utils.py

from sqlalchemy.orm import Session
from game_logic.models.game_state_db import GameStateDB
from game_logic.data.game_state import GameState, GameInfo, TurnInfo, PhaseInfo, GamePhaseName, asdict
from config import SessionLocal
import json
from datetime import datetime
from enum import Enum
from utils.game_state_logger import log_game_state  # Explicitly import logging utility
from game_logic.data.game_state import Tile, TileEntity, EntityDetail


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
        # Explicitly deserialize nested dictionaries into dataclass instances
        game_state_dict = db_entry.game_state
        
        # Explicitly reconstructing GameInfo
        game_info = GameInfo(**game_state_dict['game_info'])

        # Explicitly reconstructing TurnInfo with proper datetime parsing
        turn_started_at = game_state_dict['turn']['started_at']
        turn_info = TurnInfo(
            number=game_state_dict['turn']['number'],
            started_at=datetime.fromisoformat(turn_started_at) if turn_started_at else None
        )

        # Explicitly reconstructing PhaseInfo with proper Enum and datetime parsing
        phase_started_at = game_state_dict['phase']['started_at']
        phase_info = PhaseInfo(
            name=GamePhaseName(game_state_dict['phase']['name']),
            number=game_state_dict['phase'].get('number'),
            is_end_turn=game_state_dict['phase']['is_end_turn'],
            started_at=datetime.fromisoformat(phase_started_at) if phase_started_at else None
        )

        # Explicitly reconstructing Labyrinth Tiles and Entities
        labyrinth = {
            tile_id: Tile(
                x=tile_data['x'],
                y=tile_data['y'],
                type=tile_data['type'],
                revealed=tile_data['revealed'],
                open_directions=tile_data['open_directions'],
                effect_keyword=tile_data.get('effect_keyword'),
                entities=[
                    TileEntity(**entity) for entity in tile_data.get('entities', [])
                ],
                map_object=tile_data.get('map_object'),
                on_board=tile_data.get('on_board', False),
                tile_code=tile_data.get('tile_code', ""),
                thematic_area=tile_data.get('thematic_area', "")
            )
            for tile_id, tile_data in game_state_dict.get('labyrinth', {}).items()
        }

        # Explicitly reconstructing detailed Entities
        entities = {
            entity_id: EntityDetail(
                type=entity_data['type'],
                controlled_by_user_id=entity_data.get('controlled_by_user_id')
            )
            for entity_id, entity_data in game_state_dict.get('entities', {}).items()
        }

        # Finally, explicitly reconstructing the complete GameState
        game_state = GameState(
            game_info=game_info,
            turn=turn_info,
            phase=phase_info,
            labyrinth=labyrinth,
            entities=entities
        )
    else:
        # Explicitly initialize a default game state if none exists
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
