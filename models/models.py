from sqlalchemy.orm import DeclarativeBase, relationship
from sqlalchemy import Column, String, ForeignKey

class Base(DeclarativeBase):
    pass

class Entity(Base):
    __tablename__ = 'entities'
    id = Column(String, primary_key=True)
    name = Column(String)
    description = Column(String)

    equipment = relationship('Equipment', back_populates='entity')
    skills = relationship('Skill', back_populates='entity')
    specials = relationship('Special', back_populates='entity')

class Equipment(Base):
    __tablename__ = 'equipment'
    id = Column(String, primary_key=True)
    entity_id = Column(String, ForeignKey('entities.id'))
    name = Column(String)
    description = Column(String)

    entity = relationship('Entity', back_populates='equipment')

class Skill(Base):
    __tablename__ = 'skills'
    id = Column(String, primary_key=True)
    entity_id = Column(String, ForeignKey('entities.id'))
    name = Column(String)
    description = Column(String)

    entity = relationship('Entity', back_populates='skills')

class Special(Base):
    __tablename__ = 'specials'
    id = Column(String, primary_key=True)
    entity_id = Column(String, ForeignKey('entities.id'))
    name = Column(String)
    description = Column(String)

    entity = relationship('Entity', back_populates='specials')
