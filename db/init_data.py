import pandas as pd
from sqlalchemy.orm import sessionmaker
from models.models import Entity, Equipment, Skill, Special

def load_data(engine, df_entities, df_equipment, df_skills, df_specials):
    Session = sessionmaker(bind=engine)
    session = Session()

    # Load entities without description
    for _, row in df_entities.iterrows():
        entity = Entity(name=row['name'])
        session.add(entity)

    # Load equipment
    for _, row in df_equipment.iterrows():
        equipment = Equipment(
            name=row['name'],
            description=row['description']
        )
        session.add(equipment)

    # Load skills
    for _, row in df_skills.iterrows():
        skill = Skill(
            name=row['name'],
            description=row['description']
        )
        session.add(skill)

    # Load specials
    for _, row in df_specials.iterrows():
        special = Special(
            name=row['name'],
            description=row['description']
        )
        session.add(special)

    session.commit()
    session.close()
