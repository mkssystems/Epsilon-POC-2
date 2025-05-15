# game_logic/data/game_state.py
from dataclasses import dataclass, asdict, field
from typing import List, Optional, Dict, Any
from enum import Enum
from datetime import datetime
from models.game_state_db import GameStateDB
from sqlalchemy.orm import Session
from uuid import UUID
import json


# Enumeration explicitly defining all possible phases in the game
class GamePhaseName(Enum):
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


# Dataclass explicitly representing main game meta-information
@dataclass
class GameInfo:
    session_id: str               # Unique game session identifier
    scenario: str                 # Scenario name explicitly
    labyrinth_id: str             # Labyrinth identifier explicitly
    size: int                     # Labyrinth size explicitly
    seed: str                     # Seed used for labyrinth generation


# Dataclass explicitly representing current turn information
@dataclass
class TurnInfo:
    number: int                   # Current turn number explicitly
    started_at: datetime          # Timestamp explicitly indicating turn start


# Dataclass explicitly representing current phase information
@dataclass
class PhaseInfo:
    name: GamePhaseName           # Current phase name explicitly
    number: Optional[int]         # Sub-phase number explicitly (None if not applicable)
    is_end_turn: bool             # Explicit indicator if it's an end turn
    started_at: datetime          # Timestamp explicitly indicating phase start


# Dataclass explicitly representing individual entities placed on a tile
@dataclass
class TileEntity:
    id: str                       # Entity ID explicitly
    type: str                     # Entity type (player, enemy, npc)


# Dataclass explicitly representing each tile of the labyrinth
@dataclass
class Tile:
    x: int                        # X-coordinate explicitly
    y: int                        # Y-coordinate explicitly
    type: str                     # Tile type explicitly
    revealed: bool                # Reveal status explicitly
    open_directions: List[str]    # Explicitly open directions (e.g., ["N", "S"])
    effect_keyword: Optional[str] = None  # Effect keyword explicitly defined for tile
    entities: List[TileEntity] = field(default_factory=list)  # Entities explicitly placed
    map_object: Optional[Dict[str, str]] = None              # Map object explicitly placed


# Dataclass explicitly representing detailed entity parameters
@dataclass
class EntityDetail:
    type: str                             # Type explicitly (player, npc, enemy)
    controlled_by_user_id: Optional[str]  # Controlling user explicitly (None if AI)


# Dataclass explicitly representing the complete game state snapshot
@dataclass
class GameState:
    game_info: GameInfo                   # Main game meta-information explicitly
    turn: TurnInfo                        # Current turn information explicitly
    phase: PhaseInfo                      # Current phase information explicitly
    labyrinth: Dict[str, Tile]            # Explicit labyrinth tile data
    entities: Dict[str, EntityDetail]     # Explicit detailed entities data

    # Explicit serialization method to convert GameState to JSON-compatible dict
    def to_json(self):
        return asdict(self)


def deserialize_game_state(game_state_json: Dict[str, Any]) -> GameState:
    return GameState(
        game_info=GameInfo(**game_state_json["game_info"]),
        turn=TurnInfo(
            number=game_state_json["turn"]["number"],
            started_at=datetime.fromisoformat(game_state_json["turn"]["started_at"])
        ),
        phase=PhaseInfo(
            name=GamePhaseName(game_state_json["phase"]["name"]),
            number=game_state_json["phase"].get("number"),
            is_end_turn=game_state_json["phase"]["is_end_turn"],
            started_at=datetime.fromisoformat(game_state_json["phase"]["started_at"])
        ),
        labyrinth={tid: Tile(
            x=td["x"], y=td["y"], type=td["type"], revealed=td["revealed"],
            open_directions=td["open_directions"], effect_keyword=td.get("effect_keyword"),
            entities=[TileEntity(**e) for e in td.get("entities", [])],
            map_object=td.get("map_object")
        ) for tid, td in game_state_json["labyrinth"].items()},
        entities={eid: EntityDetail(**ed) for eid, ed in game_state_json["entities"].items()}
    )


def load_game_state_from_db(db_session: Session, session_id: UUID) -> GameState:
    session_id_str = str(session_id)

    game_state_entry = db_session.query(GameStateDB).filter(
        GameStateDB.session_id == session_id_str
    ).first()

    if not game_state_entry:
        raise ValueError(f"Game state for session '{session_id_str}' not found explicitly.")

    return deserialize_game_state(game_state_entry.game_state)
