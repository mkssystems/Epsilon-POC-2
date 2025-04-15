# db/init_data.py
import pandas as pd
from sqlalchemy.orm import Session
from models.game_entities import Entity
from models.equipment import Equipment
from models.skills import Skill
from models.specials import Special

def load_data(engine, df_entities, df_equipment, df_skills, df_specials):
    session = Session(bind=engine)

    try:
        # Load entities into the 'entities' table first (CORRECTED)
        for index, row in df_entities.iterrows():
            entity = Entity(
                id=row['id'],
                name=row['name'],
                type=row['type'],
                age=row['age'],
                role=row['role'],
                backstory_path=row['backstory_path'],
                portrait_path=row.get('portrait_path'),
                scenario=row.get('scenario', 'Epsilon267-Fulcrum Incident')
            )
            session.add(entity)

        session.commit()

        print("Entities inserted:")
        for index, row in df_entities.iterrows():
            print(f"Inserted Entity ID: {row['id']}")

        # Load equipment
        for index, row in df_equipment.iterrows():
            print(f"Inserting Equipment with entity_id: {row['entity_id']}")

            equipment = Equipment(
                id=row['id'],
                entity_id=row['entity_id'],
                name=row['name'],
                description=row['description']
            )
            session.add(equipment)

        # Load skills
        for index, row in df_skills.iterrows():
            skill = Skill(
                id=row['id'],
                entity_id=row['entity_id'],
                name=row['name'],
                description=row['description']
            )
            session.add(skill)

        # Load specials
        for index, row in df_specials.iterrows():
            special = Special(
                id=row['id'],
                entity_id=row['entity_id'],
                description=row['description']
            )
            session.add(special)

        session.commit()
        print("Data successfully loaded into the database.")

    except Exception as e:
        session.rollback()
        print(f"Error loading data: {e}")

    finally:
        session.close()
