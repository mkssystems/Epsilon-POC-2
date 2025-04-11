# npc_logic.py

from typing import Dict, Any
from .entity_base import Entity
import random

class NPC(Entity):
    """
    Explicitly defines behavior logic for Non-Player Characters (NPCs).
    """

    def __init__(self, entity_id: str, name: str, initial_tile_id: str):
        super().__init__(entity_id, name, "NPC", initial_tile_id)

    def decide_next_action(self) -> Dict[str, Any]:
        """
        Explicitly decides the next action to be performed by the NPC based on simple predefined logic.
        """
        possible_actions = ['Stay', 'Move', 'Explore']
        selected_action = random.choice(possible_actions)

        action_params = {}
        if selected_action == 'Move':
            action_params = {"to_tile": self.choose_next_tile()}
        elif selected_action == 'Explore':
            action_params = {"current_tile": self.current_tile_id}

        print(f"NPC '{self.name}' explicitly decided action '{selected_action}' with parameters {action_params}.")

        return {
            "entity_id": self.entity_id,
            "action": selected_action,
            "params": action_params
        }

    def choose_next_tile(self) -> str:
        """
        Explicitly determines the next tile to move to (placeholder logic).
        """
        # Placeholder implementation explicitly for future sophisticated logic
        next_tile = "tile_placeholder"
        print(f"NPC '{self.name}' explicitly chose next tile: {next_tile}")
        return next_tile
