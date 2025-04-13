from sqlalchemy import Column, String, Integer, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid
from .base import Base

class GameSession(Base):
    __tablename__ = "game_sessions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    seed = Column(String(100), nullable=False)
    labyrinth_id = Column(UUID(as_uuid=True), ForeignKey("labyrinths.id", ondelete="CASCADE"))
    size = Column(Integer, nullable=False)
    creator_client_id = Column(String(100), nullable=False)  # or UUID if client IDs are UUIDs
    scenario_name = Column(String(100), nullable=False)
    difficulty = Column(String(50), nullable=False)
    max_players = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    labyrinth = relationship("Labyrinth", back_populates="game_sessions")
    players = relationship("Player", back_populates="game_session", cascade="all, delete-orphan")
    connected_clients = relationship('MobileClient', back_populates='game_session', lazy='select')
