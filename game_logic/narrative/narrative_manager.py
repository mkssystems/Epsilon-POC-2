# narrative_manager.py

import random
from typing import Dict, Any, List

class NarrativeManager:
    """
    Explicitly manages dynamic generation of narrative descriptions based on game context.
    """

    def __init__(self, session_id: str):
        self.session_id = session_id

    def select_tile_variant(self, tile_id: str) -> str:
        """
        Explicitly selects a random narrative variant for the specified tile.
        """
        # Explicit placeholder for fetching tile descriptions from structured data source
        variants = self.get_tile_description_variants(tile_id)
        selected_variant = random.choice(variants)
        print(f"Selected explicit narrative variant for tile {tile_id}: {selected_variant}")
        return selected_variant

    def get_tile_description_variants(self, tile_id: str) -> List[str]:
        """
        Explicitly retrieves tile description variants (placeholder method).
        """
        # Placeholder explicitly for real implementation fetching data from XML/DB
        return [
            "You enter a dim corridor with flickering lights.",
            "The corridor is narrow and filled with a musty odor.",
            "A quiet hallway extends ahead, shrouded in shadows."
        ]

    def describe_entities_on_tile(self, tile_id: str, exclude_entity_id: str = None) -> str:
        """
        Explicitly generates descriptions for entities present on a tile.
        """
        # Explicit placeholder implementation
        entities_present = ["Captain Morgan", "A hostile alien"]
        if exclude_entity_id:
            entities_present = [e for e in entities_present if e != exclude_entity_id]

        descriptions = [f"{entity} is here." for entity in entities_present]
        entity_description = " ".join(descriptions)
        print(f"Entity descriptions explicitly generated for tile {tile_id}: {entity_description}")
        return entity_description

    def generate_tile_narrative(self, tile_id: str, player_id: str) -> str:
        """
        Explicitly combines tile and entity narratives into a full description.
        """
        tile_description = self.select_tile_variant(tile_id)
        entity_description = self.describe_entities_on_tile(tile_id, exclude_entity_id=player_id)
        
        full_narrative = f"{tile_description} {entity_description}".strip()
        print(f"Full narrative explicitly generated: {full_narrative}")
        return full_narrative
