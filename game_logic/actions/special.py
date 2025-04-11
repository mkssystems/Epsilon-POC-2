# special.py

from typing import Dict, Any
from .action_base import Action

class SpecialAction(Action):
    """
    Explicitly defines logic for special scenario-specific actions performed by entities.
    """

    def __init__(self, entity_id: str, params: Dict[str, Any]):
        super().__init__(entity_id, "Special", params)

    def validate(self) -> bool:
        """
        Explicitly validates if the special action is allowed under the current scenario conditions.
        """
        special_action_type = self.params.get("special_action_type")
        print(f"Explicitly validating special action '{special_action_type}' for entity '{self.entity_id}'.")

        # Placeholder explicitly for real validation logic
        is_valid = special_action_type is not None
        print(f"Special action validation result explicitly: {is_valid}")
        return is_valid

    def execute(self) -> Dict[str, Any]:
        """
        Explicitly executes the special action, applying unique scenario-specific effects.
        """
        if not self.validate():
            result = {
                "entity_id": self.entity_id,
                "action_type": self.action_type,
                "status": "failed",
                "reason": "Explicit special action validation failed."
            }
            print(result["reason"])
            return result

        special_action_type = self.params["special_action_type"]
        print(f"Explicitly executing special action '{special_action_type}' for entity '{self.entity_id}'.")

        # Placeholder explicitly for special action logic implementation
        special_result = {
            "entity_id": self.entity_id,
            "special_action_type": special_action_type,
            "status": "success",
            "details": f"Special action '{special_action_type}' explicitly executed by entity '{self.entity_id}'."
        }

        print(f"Special action result explicitly: {special_result}")
        return special_result

    def generate_narrative(self) -> str:
        """
        Explicitly generates narrative description of the special action.
        """
        special_action_type = self.params.get("special_action_type")
        narrative = f"Entity '{self.entity_id}' explicitly performs a special action: '{special_action_type}'."
        print(f"Explicit narrative generated for special action: {narrative}")
        return narrative
