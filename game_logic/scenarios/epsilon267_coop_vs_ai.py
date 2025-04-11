# epsilon267_coop_vs_ai.py

from .scenario_base import ScenarioBase
from typing import Dict, Any

class Epsilon267CoopVsAI(ScenarioBase):
    """
    Explicitly implements cooperative gameplay scenario where players face AI-controlled enemies.
    """

    def initialize_scenario(self) -> Dict[str, Any]:
        """
        Explicitly initializes scenario-specific entities, labyrinth configuration, and narrative context.
        """
        initial_conditions = {
            "entities": {
                "players": {
                    "player_1": {"initial_tile_id": "tile_start", "entity_type": "player"},
                    "player_2": {"initial_tile_id": "tile_start", "entity_type": "player"}
                },
                "enemies": {
                    "enemy_ai_1": {"initial_tile_id": "tile_ai_spawn", "entity_type": "Enemy"}
                }
            },
            "scenario_objective": "Reach the central control room and disable the AI core."
        }
        print("Explicitly initialized 'Coop vs AI' scenario conditions.")
        return initial_conditions

    def check_conditions(self, game_state: Dict[str, Any]) -> bool:
        """
        Explicitly checks whether the scenario's objective is achieved.
        """
        control_room_accessed = game_state.get("control_room_accessed", False)
        ai_core_disabled = game_state.get("ai_core_disabled", False)
        
        conditions_met = control_room_accessed and ai_core_disabled
        print(f"Explicitly checked scenario conditions: {conditions_met}")
        return conditions_met

    def conclude_scenario(self, game_state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Explicitly handles conclusion logic upon completing the scenario.
        """
        outcome = {
            "success": True,
            "narrative": "You've successfully disabled the AI core. The crew breathes a collective sigh of relief as the danger subsides."
        }
        print("Explicitly concluded 'Coop vs AI' scenario with success.")
        return outcome
