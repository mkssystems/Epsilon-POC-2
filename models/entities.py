from sqlalchemy import Column, String, Integer, Text
from . import Base  # Assuming Base is imported from your SQLAlchemy setup

class Entity(Base):
    __tablename__ = 'entities'
    
    id = Column(String, primary_key=True)  # Use UUID or String for the ID
    name = Column(String, nullable=False)
    type = Column(String)
    age = Column(Integer)
    role = Column(String)
    backstory_path = Column(String)  # Path to the backstory file
    
    def __repr__(self):
        return f"<Entity(name={self.name}, type={self.type}, age={self.age}, role={self.role})>"
