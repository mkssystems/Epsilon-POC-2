from sqlalchemy import Column, String, Integer, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid
from .base import Base
from db import db  # <-- This import is required to use db.relationship

class GameSession(Base):
    __tablename__ = "game_sessions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    seed = Column(String(100), nullable=False)
    labyrinth_id = Column(UUID(as_uuid=True), ForeignKey("labyrinths.id", ondelete="CASCADE"))
    start_x = Column(Integer, default=0)
    start_y = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

    labyrinth = relationship("Labyrinth", back_populates="game_sessions")
    players = relationship("Player", back_populates="game_session", cascade="all, delete-orphan")
    
    connected_clients = db.relationship('MobileClient', backref='game_session', lazy=True)
