# game_logic/data/game_state.py
from dataclasses import dataclass, asdict
from typing import List, Optional
from enum import Enum
from datetime import datetime

# Enumeration explicitly defining all possible phases in the game
class GamePhaseName(Enum):
    TURN_0 = "TURN_0"
    RETRIEVE_CURRENT_STATE = "RETRIEVE_CURRENT_STATE"
    CHECK_GAME_END_CONDITIONS = "CHECK_GAME_END_CONDITIONS"
    EXECUTE_ENVIRONMENT_LOGIC = "EXECUTE_ENVIRONMENT_LOGIC"
    DEFINE_AVAILABLE_ACTIONS = "DEFINE_AVAILABLE_ACTIONS"
    BUILD_NARRATIVE_CONTENT = "BUILD_NARRATIVE_CONTENT"
    CREATE_FPV_VISUALIZATION = "CREATE_FPV_VISUALIZATION"
    SEND_BOARD_MANIPULATION_INSTRUCTIONS = "SEND_BOARD_MANIPULATION_INSTRUCTIONS"
    PLAYER_BOARD_MANIPULATION_CONFIRMATION = "PLAYER_BOARD_MANIPULATION_CONFIRMATION"
    DISPLAY_PLAYER_DATA_POSSIBLE_ACTIONS = "DISPLAY_PLAYER_DATA_POSSIBLE_ACTIONS"
    PLAYER_ACTION_DECLARATION = "PLAYER_ACTION_DECLARATION"
    NPC_ENEMY_ACTION_DECLARATION = "NPC_ENEMY_ACTION_DECLARATION"
    UNIFIED_ACTION_RESOLUTION = "UNIFIED_ACTION_RESOLUTION"
    TURN_COMPLETION_STATE_UPDATE = "TURN_COMPLETION_STATE_UPDATE"
    INCREMENT_TURN_COUNTER = "INCREMENT_TURN_COUNTER"
    END_TURN = "END_TURN"

# Explicitly structured information about current game turn
@dataclass
class TurnInfo:
    number: int                    # Current turn number explicitly (0 = initial turn)
    started_at: datetime           # Timestamp when turn explicitly started

# Explicitly structured information about current game phase/subphase
@dataclass
class PhaseInfo:
    name: GamePhaseName            # Name of current phase explicitly from enumeration
    number: Optional[int]          # Number of current subphase explicitly, None for TURN_0 or END_TURN
    is_end_turn: bool              # Flag explicitly indicating if the game is in an End Turn phase
    started_at: datetime           # Timestamp explicitly when current phase started

# Explicitly structured information about each entity
@dataclass
class Entity:
    id: str                        # Unique identifier explicitly of entity
    type: str                      # Explicit type (player/enemy/npc)
    position: str                  # Explicit tile ID representing entity position
    controlled_by_user_id: Optional[str] = None  # User ID explicitly controlling entity (None for NPC/enemy)

# Explicitly structured complete snapshot of game state
@dataclass
class GameState:
    session_id: str                # Game session identifier explicitly
    turn: TurnInfo                 # Current turn details explicitly
    phase: PhaseInfo               # Current phase details explicitly
    labyrinth: dict                # Labyrinth structure explicitly as existing in your codebase
    entities: List[Entity]         # Explicit list of entities present in the game
