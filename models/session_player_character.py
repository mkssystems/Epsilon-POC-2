from sqlalchemy import Column, String, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from .base import Base

class SessionPlayerCharacter(Base):
    __tablename__ = 'session_player_characters'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(UUID(as_uuid=True), ForeignKey('game_sessions.id', ondelete='CASCADE'), nullable=False)
    client_id = Column(String, nullable=False)
    entity_id = Column(String, ForeignKey('entities.id'), nullable=False)
    locked = Column(Boolean, default=False)

    entity = relationship("Entity")
    session = relationship("GameSession")
