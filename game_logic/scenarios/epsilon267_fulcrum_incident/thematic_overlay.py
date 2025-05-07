# game_logic/scenarios/epsilon267_fulcrum_incident/thematic_overlay.py
from models.tile import Tile
import random
from collections import deque, defaultdict

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

# Utility function explicitly creating adjacency map based on tile coordinates
def build_adjacency_map(tiles):
    adjacency = defaultdict(list)
    positions = {(tile.x, tile.y): tile for tile in tiles}
    for tile in tiles:
        x, y = tile.x, tile.y
        # Check explicitly each neighbor direction (up, down, left, right)
        for dx, dy in [(-1,0), (1,0), (0,-1), (0,1)]:
            neighbor = positions.get((x + dx, y + dy))
            if neighbor:
                adjacency[tile].append(neighbor)
    return adjacency

# Main function explicitly assigning thematic overlays to tiles in cohesive clusters
def apply_thematic_overlay(tiles):
    total_tiles = len(tiles)

    # Calculate explicit number of tiles per thematic area
    tiles_per_theme = {
        theme: int(total_tiles * percentage)
        for theme, percentage in THEMATIC_DISTRIBUTION.items()
    }

    # Handle rounding explicitly to ensure total tile count matches
    assigned_count = sum(tiles_per_theme.values())
    remaining = total_tiles - assigned_count

    # Distribute explicitly any remaining tiles due to rounding
    for theme in THEMATIC_DISTRIBUTION.keys():
        if remaining == 0:
            break
        tiles_per_theme[theme] += 1
        remaining -= 1

    # Build adjacency map explicitly for clustering
    adjacency_map = build_adjacency_map(tiles)

    # Explicitly shuffle tiles to randomize starting points for thematic areas
    random.shuffle(tiles)

    # Set explicitly all tiles as initially unassigned
    unassigned_tiles = set(tiles)

    # Assign thematic areas explicitly using BFS for clustering
    for theme_code, count in tiles_per_theme.items():
        queue = deque()

        # Explicitly find a random starting tile from unassigned tiles
        for tile in tiles:
            if tile in unassigned_tiles:
                queue.append(tile)
                break

        # Explicitly perform BFS to assign tiles cohesively
        assigned = 0
        while queue and assigned < count:
            current_tile = queue.popleft()
            if current_tile not in unassigned_tiles:
                continue

            # Explicitly assign thematic area and tile code
            sorted_directions = ''.join(sorted(current_tile.open_directions))
            current_tile.thematic_area = THEMATIC_AREA_NAMES[theme_code]
            current_tile.tile_code = f"{theme_code}-{sorted_directions}"

            unassigned_tiles.remove(current_tile)
            assigned += 1

            # Explicitly enqueue neighbors for BFS traversal
            for neighbor in adjacency_map[current_tile]:
                if neighbor in unassigned_tiles and neighbor not in queue:
                    queue.append(neighbor)

        # In rare cases, explicitly handle if clustering didn't fully assign the required tiles
        # This could happen due to isolated clusters or rounding discrepancies
        if assigned < count:
            for tile in unassigned_tiles:
                if assigned >= count:
                    break
                sorted_directions = ''.join(sorted(tile.open_directions))
                tile.thematic_area = THEMATIC_AREA_NAMES[theme_code]
                tile.tile_code = f"{theme_code}-{sorted_directions}"
                assigned += 1
                unassigned_tiles.remove(tile)

    # Return explicitly updated tiles with thematic assignments
    return tiles
