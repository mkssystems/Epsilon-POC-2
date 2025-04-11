# fight.py

from typing import Dict, Any
from .action_base import Action
import random

class FightAction(Action):
    """
    Explicitly defines logic for fight actions performed by entities.
    """

    def __init__(self, entity_id: str, params: Dict[str, Any]):
        super().__init__(entity_id, "Fight", params)

    def validate(self) -> bool:
        """
        Explicitly validates whether the fight action can occur between entities.
        """
        target_id = self.params.get("target_id")
        print(f"Explicitly validating fight action from '{self.entity_id}' to target '{target_id}'.")

        # Placeholder explicitly for real validation logic (e.g., checking entities' positions)
        is_valid = target_id is not None
        print(f"Fight action validation result explicitly: {is_valid}")
        return is_valid

    def execute(self) -> Dict[str, Any]:
        """
        Explicitly executes the fight action, resolving combat and applying results.
        """
        if not self.validate():
            result = {
                "entity_id": self.entity_id,
                "action_type": self.action_type,
                "status": "failed",
                "reason": "Explicit fight validation failed."
            }
            print(result["reason"])
            return result

        target_id = self.params["target_id"]
        damage = random.randint(1, 5)  # Explicit placeholder for damage calculation logic
        print(f"Explicitly executing fight action: '{self.entity_id}' attacking '{target_id}' for {damage} damage.")

        # Placeholder explicitly for updating entity states (health, etc.) in game state
        result = {
            "entity_id": self.entity_id,
            "target_id": target_id,
            "action_type": self.action_type,
            "status": "success",
            "damage": damage,
            "details": f"'{self.entity_id}' explicitly dealt {damage} damage to '{target_id}'."
        }
        print(f"Fight action result explicitly: {result}")
        return result

    def generate_narrative(self) -> str:
        """
        Explicitly generates narrative description of the fight action.
        """
        target_id = self.params.get("target_id")
        narrative = f"Entity '{self.entity_id}' explicitly attacks '{target_id}'."
        print(f"Explicit narrative generated for fight action: {narrative}")
        return narrative
