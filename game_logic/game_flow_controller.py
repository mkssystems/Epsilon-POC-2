# game_logic/game_flow_controller.py
from sqlalchemy.orm import Session
from game_logic.data.game_state import GameState
from utils.db_utils import (
    save_game_state_to_db, 
    get_db_session, 
    load_initial_game_state
)
from game_logic.phases.turn_zero import execute_turn_zero

class GameFlowController:
    def __init__(self, session_id: str):
        """
        Explicitly initializes GameFlowController with session ID and retrieves initial game state.

        Args:
            session_id (str): Identifier for the current game session.
        """
        self.session_id = session_id
        self.db_session: Session = get_db_session()
        self.game_state: GameState = load_initial_game_state(self.db_session, session_id)

    def start_game(self):
        """
        Explicitly delegates Turn 0 initialization to its dedicated phase logic.
        """
        # FIXED: explicitly passing session_id instead of entire GameState object
        execute_turn_zero(self.db_session, self.session_id)

        print(f"[INFO] Game start explicitly handled by Turn 0 for session {self.session_id}")

    def advance_phase(self):
        """
        Explicit logic to advance the game to the next phase. (Further details to be added incrementally)
        """
        # Implementation of phase advancement will be explicitly detailed later
        save_game_state_to_db(self.db_session, self.game_state)
