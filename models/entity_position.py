# entity_position.py

from sqlalchemy import Column, String, Integer
from sqlalchemy.ext.declarative import declarative_base
import uuid

Base = declarative_base()

class EntityPosition(Base):
    """
    Explicitly defines the database schema for tracking entity positions within the labyrinth.
    """

    __tablename__ = 'entity_positions'

    position_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id = Column(String, index=True, nullable=False)
    labyrinth_id = Column(String, nullable=False)
    turn_number = Column(Integer, nullable=False)
    entity_type = Column(String, nullable=False)  # e.g., player, enemy, npc, object
    entity_id = Column(String, nullable=False)
    tile_id = Column(String, nullable=False)

    def __repr__(self):
        return f"<EntityPosition(entity_id='{self.entity_id}', tile_id='{self.tile_id}', turn_number={self.turn_number})>"
