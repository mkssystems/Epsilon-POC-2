from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.orm import relationship
from . import Base

class Skill(Base):
    __tablename__ = 'skills'  # Name of the table
    
    id = Column(String, primary_key=True)  # Primary key for the skill
    entity_id = Column(String, ForeignKey('entities.id'))  # Foreign key linking to the 'entities' table
    name = Column(String, nullable=False)  # Name of the skill (non-nullable)
    description = Column(String)  # Description of the skill (nullable)
    
    # Relationship to the Entity model
    entity = relationship('Entity', back_populates='skills')  # Back-population to 'Entity'

    def __repr__(self):
        return f"<Skill(name={self.name}, description={self.description})>"
