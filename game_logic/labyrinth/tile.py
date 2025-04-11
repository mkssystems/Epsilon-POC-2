# tile.py

from typing import List, Dict, Any

class Tile:
    """
    Explicitly defines the structure and properties of individual labyrinth tiles.
    """

    def __init__(self, tile_id: str, connections: List[str], description: str):
        self.tile_id = tile_id
        self.connections = connections
        self.description = description

    def add_connection(self, tile_id: str):
        """
        Explicitly adds a new connection to another tile.
        """
        if tile_id not in self.connections:
            self.connections.append(tile_id)
            print(f"Explicitly added connection from {self.tile_id} to {tile_id}.")

    def remove_connection(self, tile_id: str):
        """
        Explicitly removes a connection from this tile.
        """
        if tile_id in self.connections:
            self.connections.remove(tile_id)
            print(f"Explicitly removed connection from {self.tile_id} to {tile_id}.")

    def serialize(self) -> Dict[str, Any]:
        """
        Explicitly serializes the tile data for JSON storage.
        """
        return {
            "tile_id": self.tile_id,
            "connections": self.connections,
            "description": self.description
        }

    @staticmethod
    def deserialize(data: Dict[str, Any]) -> 'Tile':
        """
        Explicitly creates a Tile instance from serialized data.
        """
        return Tile(
            tile_id=data["tile_id"],
            connections=data["connections"],
            description=data["description"]
        )
