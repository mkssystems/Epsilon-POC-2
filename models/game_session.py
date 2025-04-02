from sqlalchemy import Column, String, Integer, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid

class GameSession(Base):
    __tablename__ = "game_sessions"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    seed = Column(String(100), nullable=False)
    labyrinth_id = Column(UUID(as_uuid=True), ForeignKey("labyrinths.id"))
    start_x = Column(Integer, default=0)  # Default starting position (x)
    start_y = Column(Integer, default=0)  # Default starting position (y)
    created_at = Column(DateTime, default=datetime.utcnow)

    labyrinth = relationship("Labyrinth", back_populates="game_sessions")
    players = relationship("Player", back_populates="game_session")

    def __repr__(self):
        return f"GameSession(id={self.id}, seed={self.seed}, created_at={self.created_at}, labyrinth_id={self.labyrinth_id})"
