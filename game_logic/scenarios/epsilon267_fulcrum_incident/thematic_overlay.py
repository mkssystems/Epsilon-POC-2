# game_logic/scenarios/epsilon267_fulcrum_incident/thematic_overlay.py
from models.tile import Tile
import random

# Explicitly defined thematic distribution percentages
THEMATIC_DISTRIBUTION = {
    'C': 0.15,  # Command
    'M': 0.35,  # Technical
    'Y': 0.30,  # Living Quarters
    'K': 0.20   # Laboratory
}

# Explicit mapping of thematic codes to thematic area names
THEMATIC_AREA_NAMES = {
    'C': 'Command',
    'M': 'Technical',
    'Y': 'Living Quarters',
    'K': 'Laboratory'
}

# Function explicitly assigning thematic overlays to tiles
def apply_thematic_overlay(tiles):
    total_tiles = len(tiles)

    # Calculate explicit number of tiles per thematic area
    tiles_per_theme = {
        theme: int(total_tiles * percentage)
        for theme, percentage in THEMATIC_DISTRIBUTION.items()
    }

    # Handle rounding explicitly to ensure total matches
    assigned_count = sum(tiles_per_theme.values())
    remaining = total_tiles - assigned_count

    # Distribute any remaining tiles explicitly
    while remaining > 0:
        for theme in THEMATIC_DISTRIBUTION.keys():
            if remaining == 0:
                break
            tiles_per_theme[theme] += 1
            remaining -= 1

    # Explicitly shuffle tiles to randomize initial thematic assignments
    random.shuffle(tiles)

    # Assign thematic areas explicitly to tiles
    tile_index = 0
    for theme_code, count in tiles_per_theme.items():
        for _ in range(count):
            tile = tiles[tile_index]
            sorted_directions = ''.join(sorted(tile.open_directions))
            tile.thematic_area = THEMATIC_AREA_NAMES[theme_code]
            tile.tile_code = f"{theme_code}-{sorted_directions}"
            tile_index += 1

    # Return explicitly updated tiles
    return tiles
