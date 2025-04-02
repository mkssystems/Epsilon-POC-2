from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from .base import Base

class Labyrinth(Base):
    __tablename__ = "labyrinths"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    size = Column(Integer)
    seed = Column(String(100), nullable=True)
    start_x = Column(Integer)
    start_y = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)

    game_sessions = relationship("GameSession", back_populates="labyrinth")
    tiles = relationship("Tile", back_populates="labyrinth")
