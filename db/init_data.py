import pandas as pd
from db import session  # Assuming session is already configured
from db.models.entity import Entity
from db.models.equipment import Equipment
from db.models.skill import Skill
from db.models.special import Special

# Load CSV Files
df_entities = pd.read_csv('assets/seed/entities.csv')
df_equipment = pd.read_csv('assets/seed/equipment.csv')
df_skills = pd.read_csv('assets/seed/skills.csv')
df_specials = pd.read_csv('assets/seed/specials.csv')

# Create Entity Instances
for index, row in df_entities.iterrows():
    entity = Entity(
        id=row['id'],
        name=row['name'],
        type=row['type'],
        age=row['age'],
        role=row['role'],
        backstory_path=row['backstory_path']
    )
    session.add(entity)

# Create Special Instances
for index, row in df_specials.iterrows():
    special = Special(
        id=row['id'],
        entity_id=row['entity_id'],
        name=row['name'],
        description=row['description']
    )
    session.add(special)

# Create Equipment Instances
for index, row in df_equipment.iterrows():
    equipment = Equipment(
        id=row['id'],
        entity_id=row['entity_id'],
        name=row['name'],
        description=row['description']
    )
    session.add(equipment)

# Create Skill Instances
for index, row in df_skills.iterrows():
    skill = Skill(
        id=row['id'],
        entity_id=row['entity_id'],
        name=row['name'],
        description=row['description'],
        level=row['level']
    )
    session.add(skill)

# Commit to DB
session.commit()
