# game_log.py

from sqlalchemy import Column, String, Integer, DateTime, Text, JSON
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
import uuid

Base = declarative_base()

class GameLog(Base):
    """
    Explicitly defines the database schema for logging detailed game events.
    """

    __tablename__ = 'game_logs'

    log_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id = Column(String, index=True, nullable=False)
    turn_number = Column(Integer, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    actor_type = Column(String, nullable=False)
    actor_id = Column(String, nullable=False)
    action_phase = Column(String, nullable=False)
    action_type = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    additional_data = Column(JSON, nullable=True)

    def __repr__(self):
        return f"<GameLog(log_id='{self.log_id}', session_id='{self.session_id}', turn_number={self.turn_number})>"
