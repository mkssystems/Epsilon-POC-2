# game_logic/data/game_state.py
from dataclasses import dataclass, asdict, field
from typing import List, Optional, Dict, Any
from enum import Enum
from datetime import datetime
from game_logic.models.game_state_db import GameStateDB
from sqlalchemy.orm import Session
from uuid import UUID
import json


class GamePhaseName(Enum):
    WAITING_FOR_PLAYERS = "WAITING_FOR_PLAYERS"
    TURN_0 = "TURN_0"
    INITIAL_PLACEMENT = "INITIAL_PLACEMENT"
    ST_RETRIEVE_CURRENT_STATE = "ST_RETRIEVE_CURRENT_STATE"
    ST_CHECK_GAME_END_CONDITIONS = "ST_CHECK_GAME_END_CONDITIONS"
    ST_EXECUTE_ENVIRONMENT_LOGIC = "ST_EXECUTE_ENVIRONMENT_LOGIC"
    ST_DEFINE_AVAILABLE_ACTIONS = "ST_DEFINE_AVAILABLE_ACTIONS"
    ST_BUILD_NARRATIVE_CONTENT = "ST_BUILD_NARRATIVE_CONTENT"
    ST_CREATE_FPV_VISUALIZATION = "ST_CREATE_FPV_VISUALIZATION"
    ST_SEND_BOARD_MANIPULATION_INSTRUCTIONS = "ST_SEND_BOARD_MANIPULATION_INSTRUCTIONS"
    ST_PLAYER_BOARD_MANIPULATION_CONFIRMATION = "ST_PLAYER_BOARD_MANIPULATION_CONFIRMATION"
    ST_DISPLAY_PLAYER_DATA_POSSIBLE_ACTIONS = "ST_DISPLAY_PLAYER_DATA_POSSIBLE_ACTIONS"
    ST_PLAYER_ACTION_DECLARATION = "ST_PLAYER_ACTION_DECLARATION"
    ST_NPC_ENEMY_ACTION_DECLARATION = "ST_NPC_ENEMY_ACTION_DECLARATION"
    ST_UNIFIED_ACTION_RESOLUTION = "ST_UNIFIED_ACTION_RESOLUTION"
    ST_TURN_COMPLETION_STATE_UPDATE = "ST_TURN_COMPLETION_STATE_UPDATE"
    ST_INCREMENT_TURN_COUNTER = "ST_INCREMENT_TURN_COUNTER"
    END_TURN = "END_TURN"


@dataclass
class GameInfo:
    session_id: str
    scenario: str
    labyrinth_id: str
    size: int
    seed: str


@dataclass
class TurnInfo:
    number: int
    started_at: Optional[datetime]


@dataclass
class PhaseInfo:
    name: GamePhaseName
    number: Optional[int]
    is_end_turn: bool
    started_at: Optional[datetime]


@dataclass
class TileEntity:
    id: str
    type: str


@dataclass
class Tile:
    x: int
    y: int
    type: str
    revealed: bool
    open_directions: List[str]
    effect_keyword: Optional[str] = None
    entities: List[TileEntity] = field(default_factory=list)
    map_object: Optional[Dict[str, str]] = None
    on_board: bool = False
    tile_code: str = ""
    thematic_area: str = ""


@dataclass
class EntityDetail:
    type: str
    controlled_by_user_id: Optional[str]


@dataclass
class GameState:
    game_info: GameInfo
    turn: TurnInfo
    phase: PhaseInfo
    labyrinth: Dict[str, Tile]
    entities: Dict[str, EntityDetail]

    def to_json(self):
        return asdict(self)


def _parse_datetime(date_str: Optional[str]) -> Optional[datetime]:
    if date_str is None:
        return None
    try:
        return datetime.fromisoformat(date_str)
    except Exception as e:
        raise ValueError(f"Failed to parse datetime explicitly: '{date_str}' - {e}")



def deserialize_game_state(game_state_json: Dict[str, Any]) -> GameState:
    try:
        game_info = GameInfo(**game_state_json["game_info"])
        turn_info = TurnInfo(
            number=game_state_json["turn"]["number"],
            started_at=_parse_datetime(game_state_json["turn"]["started_at"])
        )
        phase_info = PhaseInfo(
            name=GamePhaseName(game_state_json["phase"]["name"]),
            number=game_state_json["phase"].get("number"),
            is_end_turn=game_state_json["phase"]["is_end_turn"],
            started_at=_parse_datetime(game_state_json["phase"]["started_at"])
        )
        labyrinth = {
            tid: Tile(
                x=td["x"],
                y=td["y"],
                type=td["type"],
                revealed=td["revealed"],
                open_directions=td["open_directions"],
                effect_keyword=td.get("effect_keyword"),
                entities=[TileEntity(**e) for e in td.get("entities", [])],
                map_object=td.get("map_object")
                on_board=td.get("on_board", False),
                tile_code=td.get("tile_code", ""),
                thematic_area=td.get("thematic_area", "")
            ) for tid, td in game_state_json["labyrinth"].items()
        }
        entities = {
            eid: EntityDetail(**ed) for eid, ed in game_state_json["entities"].items()
        }
    except KeyError as ke:
        raise ValueError(f"Missing required key explicitly during deserialization: {ke}")
    except Exception as e:
        raise ValueError(f"Error explicitly during game state deserialization: {e}")

    return GameState(game_info, turn_info, phase_info, labyrinth, entities)


def load_game_state_from_db(db_session: Session, session_id: UUID) -> GameState:
    session_id_str = str(session_id)
    game_state_entry = db_session.query(GameStateDB).filter(
        GameStateDB.session_id == session_id_str
    ).first()

    if not game_state_entry:
        raise ValueError(f"Game state explicitly not found for session '{session_id_str}'.")

    try:
        return deserialize_game_state(game_state_entry.game_state)
    except Exception as e:
        raise ValueError(f"Failed explicitly to load game state from DB: {e}")
