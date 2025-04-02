from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid
from .base import Base

class Player(Base):
    __tablename__ = "players"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    game_session_id = Column(UUID(as_uuid=True), ForeignKey("game_sessions.id"), nullable=False)
    player_x = Column(Integer, default=0, nullable=False)
    player_y = Column(Integer, default=0, nullable=False)
    username = Column(String(100), nullable=True)

    game_session = relationship("GameSession", back_populates="players")
