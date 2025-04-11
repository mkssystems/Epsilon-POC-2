# epsilon267_race.py

from .scenario_base import ScenarioBase
from typing import Dict, Any

class Epsilon267Race(ScenarioBase):
    """
    Explicitly implements a competitive racing scenario where players race against time and each other.
    """

    def initialize_scenario(self) -> Dict[str, Any]:
        """
        Explicitly initializes scenario-specific entities, labyrinth configuration, and narrative context.
        """
        initial_conditions = {
            "entities": {
                "players": {
                    "player_1": {"initial_tile_id": "tile_start_p1", "entity_type": "player"},
                    "player_2": {"initial_tile_id": "tile_start_p2", "entity_type": "player"}
                },
                "scenario_timer": 30  # minutes
            },
            "scenario_objective": "Be the first to reach the evacuation shuttle before the facility self-destructs."
        }
        print("Explicitly initialized 'Race' scenario conditions.")
        return initial_conditions

    def check_conditions(self, game_state: Dict[str, Any]) -> bool:
        """
        Explicitly checks whether any player has reached the evacuation shuttle.
        """
        shuttle_reached_by = game_state.get("shuttle_reached_by", None)
        
        conditions_met = shuttle_reached_by is not None
        print(f"Explicitly checked race scenario conditions: {conditions_met}")
        return conditions_met

    def conclude_scenario(self, game_state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Explicitly handles conclusion logic upon completing the scenario.
        """
        winner = game_state.get("shuttle_reached_by")
        outcome = {
            "success": True,
            "winner": winner,
            "narrative": f"Player {winner} reaches the shuttle first, narrowly escaping as the facility explodes behind."
        }
        print("Explicitly concluded 'Race' scenario with a winner.")
        return outcome
