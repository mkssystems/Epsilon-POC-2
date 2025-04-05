# db/models/special.py
from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.orm import relationship
from . import Base

class Special(Base):
    __tablename__ = 'specials'  # Name of the table

    id = Column(String, primary_key=True)
    entity_id = Column(String, ForeignKey('entities.id'))  # Foreign key to the Entity table
    name = Column(String)
    description = Column(String)

    # Relationship to the Entity model
    entity = relationship('Entity', back_populates='specials')
