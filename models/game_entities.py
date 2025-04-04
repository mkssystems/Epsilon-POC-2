import os
import uuid
from sqlalchemy import create_engine, Column, String, Integer, ForeignKey, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

# Base setup
Base = declarative_base()

# --- Table Definitions ---

class Entity(Base):
    __tablename__ = 'entities'

    id = Column(String, primary_key=True)
    name = Column(String)
    type = Column(String)  # 'player', 'enemy', 'npc'
    origin = Column(String)
    role = Column(String)
    initiative = Column(Integer)
    weaponry = Column(Integer)
    technology = Column(Integer)
    knowledge = Column(Integer)
    armour = Column(Integer)
    life_points = Column(Integer)
    portrait_path = Column(String)
    backstory_path = Column(String)

    equipment = relationship("Equipment", back_populates="entity")
    skills = relationship("Skill", back_populates="entity")
    specials = relationship("Special", back_populates="entity")

class Equipment(Base):
    __tablename__ = 'equipment'

    id = Column(String, primary_key=True)
    entity_id = Column(String, ForeignKey('entities.id'))
    name = Column(String)
    description = Column(Text)

    entity = relationship("Entity", back_populates="equipment")

class Skill(Base):
    __tablename__ = 'skills'

    id = Column(String, primary_key=True)
    entity_id = Column(String, ForeignKey('entities.id'))
    name = Column(String)
    description = Column(Text)

    entity = relationship("Entity", back_populates="skills")

class Special(Base):
    __tablename__ = 'specials'

    id = Column(String, primary_key=True)
    entity_id = Column(String, ForeignKey('entities.id'))
    description = Column(Text)

    entity = relationship("Entity", back_populates="specials")

# --- Database Initialization ---

def init_db(uri):
    engine = create_engine(uri)
    Base.metadata.create_all(engine)
    return engine

# --- Sample Data Loader ---

def load_data(engine, df_entities, df_equipment, df_skills, df_specials):
    Session = sessionmaker(bind=engine)
    session = Session()

    # Insert Entities
    for _, row in df_entities.iterrows():
        entity = Entity(
            id=row['id'],
            name=row.get('name', ''),
            type=row.get('type', ''),
            origin=row.get('origin', ''),
            role=row.get('role', ''),
            initiative=row.get('initiative', 0),
            weaponry=row.get('weaponry', 0),
            technology=row.get('technology', 0),
            knowledge=row.get('knowledge', 0),
            armour=row.get('armour', 0),
            life_points=row.get('life_points', 0),
            portrait_path=f"assets/portraits/{row['id']}.png",
            backstory_path=f"assets/backstories/{row['id']}.md"
        )
        session.add(entity)

    # Insert Equipment
    for _, row in df_equipment.iterrows():
        eq = Equipment(
            id=row['id'],
            entity_id=row['entity_id'],
            name=row['name'],
            description=row['description']
        )
        session.add(eq)

    # Insert Skills
    for _, row in df_skills.iterrows():
        skill = Skill(
            id=row['id'],
            entity_id=row['entity_id'],
            name=row['name'],
            description=row['description']
        )
        session.add(skill)

    # Insert Specials
    for _, row in df_specials.iterrows():
        special = Special(
            id=row['id'],
            entity_id=row['entity_id'],
            description=row['description']
        )
        session.add(special)

    session.commit()
    session.close()
