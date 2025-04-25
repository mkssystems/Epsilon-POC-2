# game_logic/game_flow_controller.py
from sqlalchemy.orm import Session
from game_logic.data.game_state import GameState
from utils.db_utils import (
    save_game_state_to_db, 
    get_db_session, 
    load_initial_game_state
)

class GameFlowController:
    def __init__(self, session_id: str):
        self.session_id = session_id  # Explicitly store session identifier

        # Explicitly get a new database session for this controller
        self.db_session: Session = get_db_session()

        # Explicitly load initial game state based on session_id
        self.game_state: GameState = load_initial_game_state(self.db_session, session_id)

    def start_game(self):
        # Explicitly set the initial phase to 'turn_zero' when game starts
        self.game_state.phase = "turn_zero"
        self.game_state.turn_number = 0  # explicitly set the initial turn number

        # TODO: Implement any additional explicit initialization logic here
        # For example: populate entities, prepare labyrinth, etc.

        # Explicitly save the updated game state to the database
        save_game_state_to_db(self.db_session, self.game_state)

        # Log explicit confirmation (good practice)
        print(f"[INFO] Game started explicitly for session {self.session_id} at phase '{self.game_state.phase}'.")
    
    def advance_phase(self):
        # Explicit logic to advance the game to the next phase (existing method)
        # This method will later be detailed incrementally
        # Update phase and turn counter explicitly as needed

        # Save explicitly updated game state to the database after changes
        save_game_state_to_db(self.db_session, self.game_state)

