# stay.py

from typing import Dict, Any
from .action_base import Action

class StayAction(Action):
    """
    Explicitly defines logic for the default 'stay' action, representing no movement or interaction.
    """

    def __init__(self, entity_id: str, params: Dict[str, Any] = None):
        super().__init__(entity_id, "Stay", params or {})

    def validate(self) -> bool:
        """
        Explicitly validates if the stay action can always be executed.
        """
        # Explicitly, staying is always valid
        print(f"Explicitly validating stay action for entity '{self.entity_id}': always valid.")
        return True

    def execute(self) -> Dict[str, Any]:
        """
        Explicitly executes the stay action, representing a passive choice by the entity.
        """
        print(f"Explicitly executing stay action for entity '{self.entity_id}'. Entity remains at its current position.")

        # Explicit placeholder for any passive effects logic
        result = {
            "entity_id": self.entity_id,
            "action_type": self.action_type,
            "status": "success",
            "details": f"Entity explicitly remains in its current location."
        }

        print(f"Stay action result explicitly: {result}")
        return result

    def generate_narrative(self) -> str:
        """
        Explicitly generates narrative description of the stay action.
        """
        narrative = f"Entity '{self.entity_id}' explicitly chooses to remain still, observing their surroundings carefully."
        print(f"Explicit narrative generated for stay action: {narrative}")
        return narrative
