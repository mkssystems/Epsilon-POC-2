from sqlalchemy import Column, String, Integer
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

# Declare the base for all models
Base = declarative_base()

class Entity(Base):
    __tablename__ = 'entities'
    
    # Define columns with correct data types
    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    type = Column(String)
    age = Column(Integer)
    role = Column(String)
    backstory_path = Column(String)
    
    # Add relationships to link entities to other models (Equipment, Skill, Special)
    equipment = relationship('Equipment', back_populates='entity')
    skills = relationship('Skill', back_populates='entity')
    specials = relationship('Special', back_populates='entity')

    def __repr__(self):
        return f"<Entity(name={self.name}, type={self.type}, age={self.age}, role={self.role})>"
