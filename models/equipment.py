from sqlalchemy import Column, String, Text, ForeignKey
from sqlalchemy.orm import relationship
from . import Base  # Assuming Base is imported from your SQLAlchemy setup

class Equipment(Base):
    __tablename__ = 'equipment'
    
    id = Column(String, primary_key=True)  # Use UUID or String for the ID
    entity_id = Column(String, ForeignKey('entities.id'))  # ForeignKey reference to entities table
    name = Column(String, nullable=False)
    description = Column(Text)
    
    # Relationship to the Entity model (optional)
    entity = relationship('Entity', back_populates='equipment')
    
    def __repr__(self):
        return f"<Equipment(name={self.name}, description={self.description})>"
