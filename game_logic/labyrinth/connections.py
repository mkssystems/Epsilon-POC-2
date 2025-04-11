# connections.py

from typing import Dict, List

class ConnectionsManager:
    """
    Explicitly manages dynamic connections between labyrinth tiles.
    """

    def __init__(self, labyrinth_structure: Dict[str, List[str]]):
        """
        Initializes with an explicit dictionary representing the current labyrinth structure.
        """
        self.connections = labyrinth_structure

    def connect_tiles(self, tile_a: str, tile_b: str) -> None:
        """
        Explicitly connects two tiles.
        """
        if tile_b not in self.connections.get(tile_a, []):
            self.connections.setdefault(tile_a, []).append(tile_b)
            print(f"Explicitly connected tile {tile_a} with tile {tile_b}.")
        
        if tile_a not in self.connections.get(tile_b, []):
            self.connections.setdefault(tile_b, []).append(tile_a)
            print(f"Explicitly connected tile {tile_b} with tile {tile_a}.")

    def disconnect_tiles(self, tile_a: str, tile_b: str) -> None:
        """
        Explicitly disconnects two tiles.
        """
        if tile_b in self.connections.get(tile_a, []):
            self.connections[tile_a].remove(tile_b)
            print(f"Explicitly disconnected tile {tile_a} from tile {tile_b}.")
        
        if tile_a in self.connections.get(tile_b, []):
            self.connections[tile_b].remove(tile_a)
            print(f"Explicitly disconnected tile {tile_b} from tile {tile_a}.")

    def serialize_connections(self) -> Dict[str, List[str]]:
        """
        Explicitly serializes connections data for storage or transmission.
        """
        return self.connections

    def update_structure(self, new_structure: Dict[str, List[str]]) -> None:
        """
        Explicitly updates the entire labyrinth structure.
        """
        self.connections = new_structure
        print("Explicitly updated labyrinth connections structure.")
