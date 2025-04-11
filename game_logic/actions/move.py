# move.py

from typing import Dict, Any
from .action_base import Action

class MoveAction(Action):
    """
    Explicitly defines logic for move actions performed by entities.
    """

    def __init__(self, entity_id: str, params: Dict[str, Any]):
        super().__init__(entity_id, "Move", params)

    def validate(self) -> bool:
        """
        Explicitly validates if the move action can be executed according to game rules.
        """
        from_tile = self.params.get("from_tile")
        to_tile = self.params.get("to_tile")
        print(f"Explicitly validating move action from '{from_tile}' to '{to_tile}' for entity '{self.entity_id}'.")

        # Placeholder explicitly for real validation logic
        is_valid = from_tile is not None and to_tile is not None
        print(f"Move action validation result explicitly: {is_valid}")
        return is_valid

    def execute(self) -> Dict[str, Any]:
        """
        Explicitly executes the move action, updating entity's position.
        """
        if not self.validate():
            result = {
                "entity_id": self.entity_id,
                "action_type": self.action_type,
                "status": "failed",
                "reason": "Explicit move validation failed."
            }
            print(result["reason"])
            return result

        from_tile = self.params["from_tile"]
        to_tile = self.params["to_tile"]
        print(f"Explicitly executing move for entity '{self.entity_id}' from '{from_tile}' to '{to_tile}'.")

        # Placeholder explicitly for updating entity position in game state
        result = {
            "entity_id": self.entity_id,
            "action_type": self.action_type,
            "status": "success",
            "details": f"Entity moved explicitly from {from_tile} to {to_tile}."
        }
        print(f"Move action result explicitly: {result}")
        return result

    def generate_narrative(self) -> str:
        """
        Explicitly generates narrative description of the move action.
        """
        from_tile = self.params.get("from_tile")
        to_tile = self.params.get("to_tile")
        narrative = f"Entity '{self.entity_id}' moves explicitly from '{from_tile}' to '{to_tile}'."
        print(f"Explicit narrative generated for move action: {narrative}")
        return narrative
