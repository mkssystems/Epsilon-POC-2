import pandas as pd
from sqlalchemy.orm import Session
from models.models import Entity, Equipment, Skill, Special

def load_data(engine, df_entities, df_equipment, df_skills, df_specials):
    with Session(engine) as session:
        # Load Entities
        for _, row in df_entities.iterrows():
            entity = Entity(
                name=row['name'],
                description=row.get('description', 'No description provided')
            )
            session.add(entity)

        # Load Equipment
        for _, row in df_equipment.iterrows():
            equipment = Equipment(
                name=row['name'],
                description=row.get('description', 'No description provided')
            )
            session.add(equipment)

        # Load Skills
        for _, row in df_skills.iterrows():
            skill = Skill(
                name=row['name'],
                description=row.get('description', 'No description provided')
            )
            session.add(skill)

        # Load Specials
        for _, row in df_specials.iterrows():
            special = Special(
                name=row['name'],
                description=row.get('description', 'No description provided')
            )
            session.add(special)

        session.commit()
