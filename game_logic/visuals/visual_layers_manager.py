# visual_layers_manager.py

from typing import Dict, Any, List

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
