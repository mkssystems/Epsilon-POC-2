# db/init_data.py
import pandas as pd
from sqlalchemy.orm import Session
from models.models import Entity, Equipment, Skill, Special

# Function to load data into the database
def load_data(engine, df_entities, df_equipment, df_skills, df_specials):
    # Create session for DB interaction
    session = Session(bind=engine)

    try:
        # Load entities into the 'entities' table
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

        # Load equipment into the 'equipment' table
        for index, row in df_equipment.iterrows():
            equipment = Equipment(
                id=row['id'],
                entity_id=row['entity_id'],
                name=row['name'],
                description=row['description']
            )
            session.add(equipment)

        # Load skills into the 'skills' table
        for index, row in df_skills.iterrows():
            skill = Skill(
                id=row['id'],
                entity_id=row['entity_id'],
                name=row['name'],
                description=row['description']
            )
            session.add(skill)

        # Load specials into the 'specials' table
        for index, row in df_specials.iterrows():
            special = Special(
                id=row['id'],
                entity_id=row['entity_id'],
                description=row['description']
            )
            session.add(special)

        # Commit all changes to the database
        session.commit()
        print("Data successfully loaded into the database.")

    except Exception as e:
        # If any error occurs, roll back the transaction
        session.rollback()
        print(f"Error loading data: {e}")

    finally:
        # Close the session
        session.close()
