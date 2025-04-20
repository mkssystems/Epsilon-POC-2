# Explicitly integrate DB saving into game_flow_controller.py
from utils.db_utils import save_game_state_to_db

class GameFlowController:
    def __init__(self, db_session: Session, initial_game_state: GameState):
        self.db_session = db_session
        self.game_state = initial_game_state
        # Explicit additional initialization here...

    def advance_phase(self):
        # Explicitly existing logic for advancing phases...

        # Explicitly update database after each phase change:
        save_game_state_to_db(self.db_session, self.game_state)
