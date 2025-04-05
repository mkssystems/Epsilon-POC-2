from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.orm import relationship
from . import Base

class Special(Base):
    __tablename__ = 'specials'  # Name of the table

    id = Column(String, primary_key=True)  # Unique ID for the special
    entity_id = Column(String, ForeignKey('entities.id'))  # Foreign key linking to 'entities' table
    description = Column(String)  # Description of the special (consider using 'Text' if longer descriptions are needed)

    # Relationship to the Entity model
    entity = relationship('Entity', back_populates='specials')  # Back-population to 'Entity'

    def __repr__(self):
        return f"<Special(description={self.description})>"
