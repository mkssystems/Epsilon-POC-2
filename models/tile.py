from sqlalchemy import Column, Integer, String, ForeignKey, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from .base import Base
import uuid

class Tile(Base):
    __tablename__ = "tiles"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    labyrinth_id = Column(UUID(as_uuid=True), ForeignKey("labyrinths.id"), nullable=False)
    x = Column(Integer, nullable=False)
    y = Column(Integer, nullable=False)
    type = Column(String(100), nullable=False)
    open_directions = Column(String(100), nullable=False)
    revealed = Column(Boolean, nullable=False, default=False)  # Added revealed column

    labyrinth = relationship("Labyrinth", back_populates="tiles")
