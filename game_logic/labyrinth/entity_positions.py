# entity_positions.py

from models.entity_position import EntityPosition
from db.session import get_session
import uuid
from typing import List, Dict

class EntityPositions:
    """
    Explicitly manages tracking and updating positions of entities within the labyrinth.
    """

    def __init__(self, session_id: str, labyrinth_id: str):
        self.session_id = session_id
        self.labyrinth_id = labyrinth_id

    def track_entity_position(self, turn_number: int, entity_id: str, entity_type: str, tile_id: str):
        """
        Explicitly records an entity's position in the database.
        """
        position_entry = EntityPosition(
            position_id=str(uuid.uuid4()),
            session_id=self.session_id,
            labyrinth_id=self.labyrinth_id,
            turn_number=turn_number,
            entity_type=entity_type,
            entity_id=entity_id,
            tile_id=tile_id
        )

        with get_session() as db:
            db.add(position_entry)
            db.commit()
        print(f"Explicitly tracked position for entity '{entity_id}' at tile '{tile_id}' for turn '{turn_number}'.")

    def get_entity_positions(self, turn_number: int) -> List[Dict[str, str]]:
        """
        Explicitly retrieves all entity positions for a specific turn.
        """
        with get_session() as db:
            positions = db.query(EntityPosition).filter_by(
                session_id=self.session_id,
                labyrinth_id=self.labyrinth_id,
                turn_number=turn_number
            ).all()

            position_data = [{
                "entity_id": pos.entity_id,
                "entity_type": pos.entity_type,
                "tile_id": pos.tile_id
            } for pos in positions]

        print(f"Explicitly retrieved entity positions for turn '{turn_number}': {position_data}")
        return position_data
