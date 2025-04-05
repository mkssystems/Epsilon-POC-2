from sqlalchemy.orm import relationship

class Entity(Base):
    __tablename__ = 'entities'
    
    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    type = Column(String)
    age = Column(Integer)
    role = Column(String)
    backstory_path = Column(String)
    
    # Add this relationship to link entities to equipment
    equipment = relationship('Equipment', back_populates='entity')

    # Relationship to the Skill model
    skills = relationship('Skill', back_populates='entity')

    def __repr__(self):
        return f"<Entity(name={self.name}, type={self.type}, age={self.age}, role={self.role})>"
