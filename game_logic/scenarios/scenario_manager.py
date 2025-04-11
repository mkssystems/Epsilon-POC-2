# scenario_manager.py

from .epsilon267_coop_vs_ai import Epsilon267CoopVsAI
from .epsilon267_race import Epsilon267Race
from typing import Dict, Any

class ScenarioManager:
    """
    Explicitly initializes, manages, and concludes scenarios within game sessions.
    """

    def __init__(self, session_id: str, scenario_id: str):
        self.session_id = session_id
        self.scenario_id = scenario_id
        self.scenario = self._initialize_scenario()

    def _initialize_scenario(self):
        """
        Explicitly creates a scenario instance based on the provided scenario ID.
        """
        if self.scenario_id == "epsilon267_coop_vs_ai":
            return Epsilon267CoopVsAI(self.scenario_id, self.session_id)
        elif self.scenario_id == "epsilon267_race":
            return Epsilon267Race(self.scenario_id, self.session_id)
        else:
            raise ValueError(f"Scenario '{self.scenario_id}' is not explicitly defined.")

    def start_scenario(self) -> Dict[str, Any]:
        """
        Explicitly starts the scenario and returns initial conditions.
        """
        conditions = self.scenario.initialize_scenario()
        print(f"Explicitly started scenario '{self.scenario_id}'.")
        return conditions

    def evaluate_scenario_conditions(self, game_state: Dict[str, Any]) -> bool:
        """
        Explicitly evaluates scenario-specific conditions.
        """
        conditions_met = self.scenario.check_conditions(game_state)
        print(f"Explicitly evaluated scenario '{self.scenario_id}' conditions: {conditions_met}")
        return conditions_met

    def conclude_scenario(self, game_state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Explicitly concludes the scenario and returns the outcome.
        """
        outcome = self.scenario.conclude_scenario(game_state)
        print(f"Explicitly concluded scenario '{self.scenario_id}'.")
        return outcome
