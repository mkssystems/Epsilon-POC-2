# models/specials.py
from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.orm import relationship
from models.base import Base  # Correct import for Base from models.base

class Special(Base):
    __tablename__ = 'specials'  # Name of the table

    id = Column(String, primary_key=True)
    entity_id = Column(String, ForeignKey('entities.id'))  # Foreign key to the Entity table
    description = Column(String)

    # Relationship to the Entity model
    entity = relationship('Entity', back_populates='specials')
