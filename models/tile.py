# models/tile.py
from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from .base import Base
import uuid

class Tile(Base):
    __tablename__ = "tiles"

    # Unique identifier for each tile
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Identifier linking the tile to its labyrinth
    labyrinth_id = Column(UUID(as_uuid=True), ForeignKey("labyrinths.id"), nullable=False)

    # X-coordinate of tile within the labyrinth grid
    x = Column(Integer, nullable=False)

    # Y-coordinate of tile within the labyrinth grid
    y = Column(Integer, nullable=False)

    # Type of tile (e.g., "corridor", "junction", etc.)
    type = Column(String(100), nullable=False)

    # Open directions indicating possible passages (stored explicitly as JSON)
    open_directions = Column(JSON, nullable=False)

    # Indicates whether the tile has been revealed to players
    revealed = Column(Boolean, nullable=False, default=False)

    # Thematic overlay identifier combining theme (CMYK) and open directions (e.g., "C-NS", "M-EW")
    tile_code = Column(String(10), nullable=False)

    # Name of thematic area (e.g., "Command", "Technical", "Living Quarters", "Laboratory")
    thematic_area = Column(String(50), nullable=False)

    # Relationship explicitly linking back to the parent Labyrinth model
    labyrinth = relationship("Labyrinth", back_populates="tiles")
