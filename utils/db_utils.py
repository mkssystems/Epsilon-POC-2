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
from models.tile import Tile as TileDB
import uuid




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
        # Deserialize existing game_state for basic info
        game_state_dict = db_entry.game_state
        
        # Explicitly reconstruct GameInfo
        game_info = GameInfo(**game_state_dict['game_info'])

        # Explicitly reconstruct TurnInfo
        turn_started_at = game_state_dict['turn']['started_at']
        turn_info = TurnInfo(
            number=game_state_dict['turn']['number'],
            started_at=datetime.fromisoformat(turn_started_at) if turn_started_at else None
        )

        # Explicitly reconstruct PhaseInfo
        phase_started_at = game_state_dict['phase']['started_at']
        phase_info = PhaseInfo(
            name=GamePhaseName(game_state_dict['phase']['name']),
            number=game_state_dict['phase'].get('number'),
            is_end_turn=game_state_dict['phase']['is_end_turn'],
            started_at=datetime.fromisoformat(phase_started_at) if phase_started_at else None
        )

        # Explicitly fetch fresh Tile data directly from DB
        tiles_from_db = session.query(TileDB).filter_by(labyrinth_id=game_info.labyrinth_id).all()

        labyrinth = {
            str(tile.id): Tile(
                x=tile.x,
                y=tile.y,
                type=tile.type,
                revealed=tile.revealed,
                open_directions=tile.open_directions,
                entities=[
                    TileEntity(**{
                        key: str(value) if isinstance(value, Enum) or isinstance(value, datetime) or isinstance(value, uuid.UUID) else value
                        for key, value in entity.items()
                    }) 
                    for entity in game_state_dict.get('labyrinth', {}).get(str(tile.id), {}).get('entities', [])
                ],
                map_object={
                    key: str(value) if isinstance(value, uuid.UUID) else value
                    for key, value in game_state_dict.get('labyrinth', {}).get(str(tile.id), {}).get('map_object', {}).items()
                } if game_state_dict.get('labyrinth', {}).get(str(tile.id), {}).get('map_object') else None,
                on_board=tile.on_board,
                tile_code=tile.tile_code,
                thematic_area=tile.thematic_area
            )
            for tile in tiles_from_db
        }

        # Explicitly reconstruct detailed Entities
        entities = {
            str(entity_id): EntityDetail(
                type=entity_data['type'],
                controlled_by_user_id=entity_data.get('controlled_by_user_id')
            )
            for entity_id, entity_data in game_state_dict.get('entities', {}).items()
        }

        # Explicitly reconstruct final GameState
        game_state = GameState(
            game_info=game_info,
            turn=turn_info,
            phase=phase_info,
            labyrinth=labyrinth,
            entities=entities
        )

        # Explicitly save updated state back to DB
        save_game_state_to_db(session, game_state)

    else:
        # Initialize default state if no entry exists
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
