# models/game_entities.py
from sqlalchemy import Column, String, Integer
from sqlalchemy.orm import relationship
from models.base import Base  # Correct import for Base from models.base

class Entity(Base):
    __tablename__ = 'entities'
    
    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    type = Column(String)
    age = Column(String)
    role = Column(String)
    backstory_path = Column(String)
    portrait_path = Column(String)  # Existing column
    scenario = Column(String, nullable=False, default='Epsilon267-Fulcrum Incident')  # New scenario column
    
    # Relationships
    equipment = relationship('Equipment', back_populates='entity')
    skills = relationship('Skill', back_populates='entity')
    specials = relationship('Special', back_populates='entity')

    def __repr__(self):
        return f"<Entity(name={self.name}, type={self.type}, age={self.age}, role={self.role}, scenario={self.scenario})>"
