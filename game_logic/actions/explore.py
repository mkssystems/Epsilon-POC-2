# explore.py

from typing import Dict, Any
from .action_base import Action

class ExploreAction(Action):
    """
    Explicitly defines logic for explore actions performed by entities.
    """

    def __init__(self, entity_id: str, params: Dict[str, Any]):
        super().__init__(entity_id, "Explore", params)

    def validate(self) -> bool:
        """
        Explicitly validates if the explore action can be executed according to game rules.
        """
        current_tile = self.params.get("current_tile")
        print(f"Explicitly validating explore action on tile '{current_tile}' for entity '{self.entity_id}'.")

        # Placeholder explicitly for real validation logic
        is_valid = current_tile is not None
        print(f"Explore action validation result explicitly: {is_valid}")
        return is_valid

    def execute(self) -> Dict[str, Any]:
        """
        Explicitly executes the explore action, revealing discoveries or items.
        """
        if not self.validate():
            result = {
                "entity_id": self.entity_id,
                "action_type": self.action_type,
                "status": "failed",
                "reason": "Explicit explore validation failed."
            }
            print(result["reason"])
            return result

        current_tile = self.params["current_tile"]
        print(f"Explicitly executing explore action for entity '{self.entity_id}' on tile '{current_tile}'.")

        # Placeholder explicitly for exploration logic implementation
        discovery_result = {
            "entity_id": self.entity_id,
            "tile": current_tile,
            "discovery": "Ancient Artifact",
            "status": "success",
            "details": f"Entity explicitly discovered 'Ancient Artifact' on tile '{current_tile}'."
        }

        print(f"Explore action result explicitly: {discovery_result}")
        return discovery_result

    def generate_narrative(self) -> str:
        """
        Explicitly generates narrative description of the explore action.
        """
        current_tile = self.params.get("current_tile")
        narrative = f"Entity '{self.entity_id}' explicitly explores tile '{current_tile}' and discovers something intriguing."
        print(f"Explicit narrative generated for explore action: {narrative}")
        return narrative
