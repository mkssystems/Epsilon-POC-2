# game_logic/models/game_state_db.py
from sqlalchemy import Column, String, DateTime, func
from sqlalchemy.dialects.postgresql import JSONB
from models.base import Base  # Your existing SQLAlchemy Base model

# Database model explicitly representing the game state in PostgreSQL
class GameStateDB(Base):
    __tablename__ = 'game_states'

    session_id = Column(String, primary_key=True)  # Unique session/game ID
    game_state = Column(JSONB, nullable=False)     # Complete serialized game state as JSON
    updated_at = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now())  # Auto-managed timestamp

