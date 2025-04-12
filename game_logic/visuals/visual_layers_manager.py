# visual_layers_manager.py

from typing import Dict, Any, List
from models import game_entities, labyrinth
from utils import entity_positions

class VisualLayersManager:
    """
    Explicitly manages dynamic generation of visual layering instructions for the mobile client.
    """

    def __init__(self, session_id: str):
        self.session_id = session_id

    def generate_visual_layers(self, tile_id: str, entities: List[Dict[str, Any]], objects: List[str]) -> Dict[str, Any]:
        """
        Explicitly generates structured visual layering instructions based on tile, entities, and objects.
        """
        visual_instructions = {
            "base_layer": f"tiles/{tile_id}.png",
            "layers": []
        }

        for entity in entities:
            entity_layer = {
                "image": f"entities/{entity['entity_id']}.png",
                "position": entity.get("position", "center")
            }
            visual_instructions["layers"].append(entity_layer)

        for obj in objects:
            object_layer = {
                "image": f"objects/{obj}.png",
                "position": "bottom"
            }
            visual_instructions["layers"].append(object_layer)

        print(f"Explicit visual layers instructions generated: {visual_instructions}")
        return visual_instructions

    def generate_environmental_effect_layer(self, effect_id: str) -> Dict[str, Any]:
        """
        Explicitly generates visual layering instructions for environmental effects.
        """
        effect_instruction = {
            "image": f"effects/{effect_id}.png",
            "position": "overlay"
        }
        print(f"Environmental effect layer explicitly generated: {effect_instruction}")
        return effect_instruction

    def prepare_initial_visual_instructions(session_id: str, scenario_id: str, player_positions: Dict[str, str]) -> Dict[str, Any]:
        """
        Explicitly generates player-specific visual layering instructions based on their positions.
        """
        player_visual_instructions = {}
    
        for player_id, tile_id in player_positions.items():
            visual_instruction = {
                "base_layer": f"tiles/{tile_id}.png",
                "layers": []
            }
    
            # Explicitly fetch entities on tile excluding current player
            entities_present = entity_positions.get_entities_on_tile(session_id, tile_id, exclude_entity_id=player_id)
    
            for entity in entities_present:
                entity_data = game_entities.get_entity_data(entity['entity_id'])
                visual_instruction["layers"].append({
                    "image": f"entities/{entity_data.image_filename}",
                    "position": entity.get('position', 'center')  # default to center if position not specified
                })
    
            # Explicitly add environmental effects if applicable (assuming a method exists)
            environmental_effects = labyrinth.get_environmental_effects(tile_id)
            for effect in environmental_effects:
                visual_instruction["layers"].append({
                    "image": f"effects/{effect.image_filename}",
                    "position": effect.get('position', 'full-overlay')
                })
    
            player_visual_instructions[player_id] = visual_instruction
    
        return player_visual_instructions
