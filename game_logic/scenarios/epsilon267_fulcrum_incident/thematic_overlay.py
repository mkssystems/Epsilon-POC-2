# game_logic/scenarios/epsilon267_fulcrum_incident/thematic_overlay.py
from models.tile import Tile
import random
from collections import deque, defaultdict

# Explicitly defined thematic distribution percentages for different sections of the labyrinth
THEMATIC_DISTRIBUTION = {
    'C': 0.15,  # Command section (15% of tiles)
    'M': 0.35,  # Technical section (35% of tiles)
    'Y': 0.30,  # Living Quarters (30% of tiles)
    'K': 0.20   # Laboratory section (20% of tiles)
}

# Mapping of thematic codes to their corresponding human-readable names
THEMATIC_AREA_NAMES = {
    'C': 'Command',
    'M': 'Technical',
    'Y': 'Living Quarters',
    'K': 'Laboratory'
}

# Utility function that creates an adjacency map based on the tile coordinates.
# It helps identify neighboring tiles efficiently during thematic assignment.
def build_adjacency_map(tiles):
    adjacency = defaultdict(list)
    positions = {(tile.x, tile.y): tile for tile in tiles}
    for tile in tiles:
        x, y = tile.x, tile.y
        # Check explicitly each of the four neighbor directions: up, down, left, and right
        for dx, dy in [(-1,0), (1,0), (0,-1), (0,1)]:
            neighbor = positions.get((x + dx, y + dy))
            if neighbor:
                adjacency[tile].append(neighbor)
    return adjacency

# Main function responsible for assigning thematic overlays to tiles.
# Ensures tiles form cohesive thematic clusters and assigns each a unique identifier.
def apply_thematic_overlay(tiles):
    total_tiles = len(tiles)

    # Calculate explicitly how many tiles each thematic area should have
    tiles_per_theme = {
        theme: int(total_tiles * percentage)
        for theme, percentage in THEMATIC_DISTRIBUTION.items()
    }

    # Adjust explicitly for any rounding errors to ensure correct total tile count
    assigned_count = sum(tiles_per_theme.values())
    remaining = total_tiles - assigned_count

    for theme in THEMATIC_DISTRIBUTION.keys():
        if remaining == 0:
            break
        tiles_per_theme[theme] += 1
        remaining -= 1

    # Build adjacency map to facilitate BFS-based clustering
    adjacency_map = build_adjacency_map(tiles)
    
    # Shuffle tiles randomly to randomize starting points for thematic clusters
    random.shuffle(tiles)
    unassigned_tiles = set(tiles)

    # Initialize explicit counter for assigning unique numbers to tiles
    tile_number_counter = 1

    # Iterate explicitly over each thematic area to create clusters
    for theme_code, count in tiles_per_theme.items():
        queue = deque()

        # Explicitly select a random starting tile from the set of unassigned tiles
        for tile in tiles:
            if tile in unassigned_tiles:
                queue.append(tile)
                break

        assigned = 0
        # BFS explicitly ensures cohesive thematic clustering
        while queue and assigned < count:
            current_tile = queue.popleft()
            if current_tile not in unassigned_tiles:
                continue

            sorted_directions = ''.join(sorted(current_tile.open_directions))
            current_tile.thematic_area = THEMATIC_AREA_NAMES[theme_code]
            current_tile.tile_code = f"{theme_code}-{sorted_directions}-{tile_number_counter}"

            # Increment explicit numbering counter to ensure uniqueness
            tile_number_counter += 1

            unassigned_tiles.remove(current_tile)
            assigned += 1

            # Add neighbors explicitly to queue for thematic expansion
            for neighbor in adjacency_map[current_tile]:
                if neighbor in unassigned_tiles and neighbor not in queue:
                    queue.append(neighbor)

        # Handle cases explicitly where BFS couldn't assign the required tile count
        if assigned < count:
            for tile in unassigned_tiles.copy():
                if assigned >= count:
                    break
                sorted_directions = ''.join(sorted(tile.open_directions))
                tile.thematic_area = THEMATIC_AREA_NAMES[theme_code]
                tile.tile_code = f"{theme_code}-{sorted_directions}-{tile_number_counter}"
                tile_number_counter += 1
                assigned += 1
                unassigned_tiles.remove(tile)

    # Explicit final pass ensuring no tiles remain unassigned, using default theme if necessary
    if unassigned_tiles:
        default_theme_code = 'M'  # Technical theme as the fallback default
        for tile in unassigned_tiles:
            sorted_directions = ''.join(sorted(tile.open_directions))
            tile.thematic_area = THEMATIC_AREA_NAMES[default_theme_code]
            tile.tile_code = f"{default_theme_code}-{sorted_directions}-{tile_number_counter}"
            tile_number_counter += 1

    return tiles
