from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid
from .base import Base  # Import Base here!

class Player(Base):
    __tablename__ = "players"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    game_session_id = Column(UUID(as_uuid=True), ForeignKey("game_sessions.id"))
    player_x = Column(Integer, default=0)
    player_y = Column(Integer, default=0)
    username = Column(String(100), nullable=True)

    game_session = relationship("GameSession", back_populates="players")
