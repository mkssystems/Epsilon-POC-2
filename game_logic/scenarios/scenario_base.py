# scenario_base.py

from typing import Dict, Any

class ScenarioBase:
    """
    Explicitly defines a base interface for all game scenarios.
    """

    def __init__(self, scenario_id: str, session_id: str):
        self.scenario_id = scenario_id
        self.session_id = session_id

    def initialize_scenario(self) -> Dict[str, Any]:
        """
        Explicitly initializes scenario-specific conditions and entities.
        Must be implemented by subclasses.
        """
        raise NotImplementedError("Explicitly implement initialize_scenario in subclass.")

    def check_conditions(self, game_state: Dict[str, Any]) -> bool:
        """
        Explicitly evaluates whether the scenario-specific end conditions are met.
        Must be implemented by subclasses.
        """
        raise NotImplementedError("Explicitly implement check_conditions in subclass.")

    def conclude_scenario(self, game_state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Explicitly handles scenario-specific conclusion logic.
        Must be implemented by subclasses.
        """
        raise NotImplementedError("Explicitly implement conclude_scenario in subclass.")
