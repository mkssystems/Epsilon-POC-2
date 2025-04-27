from sqlalchemy import Column, String
from sqlalchemy.dialects.postgresql import UUID
import uuid
from .base import Base

class MapObject(Base):
    __tablename__ = 'map_objects'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    scenario = Column(String, nullable=False)
