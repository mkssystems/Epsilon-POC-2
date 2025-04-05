# models/skills.py
from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.orm import relationship
from models.base import Base  # Correct import for Base from models.base

class Skill(Base):
    __tablename__ = 'skills'  # Name of the table

    id = Column(String, primary_key=True)
    entity_id = Column(String, ForeignKey('entities.id'))  # Foreign key to the Entity table
    name = Column(String)
    description = Column(String)
    
    # Relationship to the Entity model
    entity = relationship('Entity', back_populates='skills')
