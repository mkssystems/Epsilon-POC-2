from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from .base import Base
import uuid

class Tile(Base):
    __tablename__ = "tiles"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    labyrinth_id = Column(UUID(as_uuid=True), ForeignKey("labyrinths.id"))
    x = Column(Integer)
    y = Column(Integer)
    type = Column(String(50))
    open_directions = Column(String(10))
