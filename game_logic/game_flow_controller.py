# game_logic/game_flow_controller.py
from sqlalchemy.orm import Session  # Explicit import for SQLAlchemy Session
from game_logic.data.game_state import GameState  # Explicit import of GameState structure
from utils.db_utils import save_game_state_to_db  # Explicit import of DB save function

class GameFlowController:
    def __init__(self, db_session: Session, initial_game_state: GameState):
        self.db_session = db_session                  # Explicitly store database session
        self.game_state = initial_game_state          # Explicitly store initial game state

    def advance_phase(self):
        # TODO: Explicitly implement logic here to advance to the next game phase
        # e.g., update self.game_state.phase to next subphase
        # and update turn counter explicitly if necessary
        
        # After explicitly updating the game_state, save it to the database:
        save_game_state_to_db(self.db_session, self.game_state)
