# game_state.py

from typing import Dict, Any

class GameState:
    """
    Explicitly stores and manages centralized game state data.
    """

    def __init__(self):
        self.state_data = {}

    def set_state(self, key: str, value: Any):
        """
        Explicitly sets a value for a specific state key.
        """
        self.state_data[key] = value
        print(f"Explicitly set state '{key}' to '{value}'.")

    def get_state(self, key: str) -> Any:
        """
        Explicitly retrieves a value for a specific state key.
        """
        value = self.state_data.get(key, None)
        print(f"Explicitly retrieved state '{key}': '{value}'.")
        return value

    def serialize_state(self) -> Dict[str, Any]:
        """
        Explicitly serializes the entire game state data.
        """
        print("Explicitly serialized game state.")
        return self.state_data

    def load_state(self, state_data: Dict[str, Any]):
        """
        Explicitly loads state data from serialized form.
        """
        self.state_data = state_data
        print("Explicitly loaded game state data.")
