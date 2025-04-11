# state_manager.py

from .game_state import GameState
import json
from db.session import get_session
from models.labyrinth import Labyrinth

class StateManager:
    """
    Explicitly manages updates and persistence of the central game state.
    """

    def __init__(self, session_id: str, labyrinth_id: str):
        self.session_id = session_id
        self.labyrinth_id = labyrinth_id
        self.game_state = GameState()

    def save_game_state(self):
        """
        Explicitly saves the serialized game state to the database.
        """
        state_json = json.dumps(self.game_state.serialize_state())

        with get_session() as db:
            labyrinth = db.query(Labyrinth).filter_by(
                session_id=self.session_id,
                id=self.labyrinth_id
            ).first()

            if labyrinth:
                labyrinth.generated_tiles = state_json
                db.commit()
                print(f"Explicitly saved game state for session '{self.session_id}'.")

    def load_game_state(self):
        """
        Explicitly loads the serialized game state from the database.
        """
        with get_session() as db:
            labyrinth = db.query(Labyrinth).filter_by(
                session_id=self.session_id,
                id=self.labyrinth_id
            ).first()

            if labyrinth and labyrinth.generated_tiles:
                state_data = json.loads(labyrinth.generated_tiles)
                self.game_state.load_state(state_data)
                print(f"Explicitly loaded game state for session '{self.session_id}'.")
            else:
                print("Explicitly no saved game state found, starting with default state.")
