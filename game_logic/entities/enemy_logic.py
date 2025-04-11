# enemy_logic.py

from typing import Dict, Any
from .entity_base import Entity
import random

class Enemy(Entity):
    """
    Explicitly defines behavior logic for enemy entities within the game.
    """

    def __init__(self, entity_id: str, name: str, initial_tile_id: str):
        super().__init__(entity_id, name, "Enemy", initial_tile_id)

    def decide_next_action(self, player_positions: Dict[str, str]) -> Dict[str, Any]:
        """
        Explicitly decides the enemy's next action based on player positions or predefined logic.
        """
        if self.current_tile_id in player_positions.values():
            selected_action = 'Fight'
            target_player_id = self.identify_target_player(player_positions)
            action_params = {"target_player_id": target_player_id}
        else:
            selected_action = 'Move'
            action_params = {"to_tile": self.choose_next_tile()}

        print(f"Enemy '{self.name}' explicitly decided action '{selected_action}' with parameters {action_params}.")

        return {
            "entity_id": self.entity_id,
            "action": selected_action,
            "params": action_params
        }

    def identify_target_player(self, player_positions: Dict[str, str]) -> str:
        """
        Explicitly identifies the target player on the current tile (placeholder logic).
        """
        for player_id, tile_id in player_positions.items():
            if tile_id == self.current_tile_id:
                print(f"Enemy '{self.name}' explicitly identified target player: {player_id}")
                return player_id
        return ""

    def choose_next_tile(self) -> str:
        """
        Explicitly determines the next tile to move to if no player is present (placeholder logic).
        """
        # Placeholder implementation explicitly for future advanced enemy movement logic
        next_tile = "tile_placeholder_enemy"
        print(f"Enemy '{self.name}' explicitly chose next tile: {next_tile}")
        return next_tile
