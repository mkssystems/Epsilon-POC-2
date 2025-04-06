from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid
from .base import Base

class MobileClient(Base):
    __tablename__ = "mobile_clients"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    client_id = Column(String(255), unique=True, nullable=False)
    connected_at = Column(DateTime, default=datetime.utcnow)
    game_session_id = Column(UUID(as_uuid=True), ForeignKey("game_sessions.id", ondelete="CASCADE"))

    game_session = relationship("GameSession", back_populates="connected_clients")
