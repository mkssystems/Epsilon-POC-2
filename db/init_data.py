import pandas as pd
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from models import Entity, Equipment, Skill, Special  # Updated import path

def load_data(engine, df_entities, df_equipment, df_skills, df_specials):
    with Session(engine) as session:
        # Load entities
        for _, row in df_entities.iterrows():
            entity = Entity(
                id=row['id'],
                name=row['name'],
                description=row['description']
            )
            session.add(entity)

        # Load equipment
        for _, row in df_equipment.iterrows():
            equipment = Equipment(
                id=row['id'],
                entity_id=row['entity_id'],
                name=row['name'],
                description=row['description']
            )
            session.add(equipment)

        # Load skills
        for _, row in df_skills.iterrows():
            skill = Skill(
                id=row['id'],
                entity_id=row['entity_id'],
                name=row['name'],
                description=row['description']
            )
            session.add(skill)

        # Load specials
        for _, row in df_specials.iterrows():
            special = Special(
                id=row['id'],
                entity_id=row['entity_id'],
                name=row['name'],
                description=row['description']
            )
            session.add(special)

        session.commit()

# Example usage
if __name__ == "__main__":
    engine = create_engine('your_database_connection_string')

    # Load data from CSV files
    df_entities = pd.read_csv('path_to_entities.csv')
    df_equipment = pd.read_csv('path_to_equipment.csv')
    df_skills = pd.read_csv('path_to_skills.csv')
    df_specials = pd.read_csv('path_to_specials.csv')

    load_data(engine, df_entities, df_equipment, df_skills, df_specials)
