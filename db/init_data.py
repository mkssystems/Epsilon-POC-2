# db/init_data.py
import pandas as pd
from sqlalchemy.orm import Session
from models.game_entities import Entity
from models.equipment import Equipment
from models.skills import Skill
from models.specials import Special
from models.map_object import MapObject  # explicitly import the new MapObject model

def load_data(engine, df_entities, df_equipment, df_skills, df_specials, df_map_objects):
    session = Session(bind=engine)

    try:
        # Load entities into the 'entities' table
        for _, row in df_entities.iterrows():
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
        print("Entities successfully inserted into the database.")

        # Load equipment linked to entities
        for _, row in df_equipment.iterrows():
            equipment = Equipment(
                id=row['id'],
                entity_id=row['entity_id'],
                name=row['name'],
                description=row['description']
            )
            session.add(equipment)

        # Load skills linked to entities
        for _, row in df_skills.iterrows():
            skill = Skill(
                id=row['id'],
                entity_id=row['entity_id'],
                name=row['name'],
                description=row['description']
            )
            session.add(skill)

        # Load specials linked to entities
        for _, row in df_specials.iterrows():
            special = Special(
                id=row['id'],
                entity_id=row['entity_id'],
                description=row['description']
            )
            session.add(special)

        # Explicitly load map objects
        for _, row in df_map_objects.iterrows():
            map_object = MapObject(
                id=row['id'],
                name=row['name'],
                description=row['description'],
                scenario=row['scenario']
            )
            session.add(map_object)

        session.commit()
        print("Equipment, skills, specials, and map objects successfully loaded into the database.")

    except Exception as e:
        session.rollback()
        print(f"Error occurred during data loading: {e}")

    finally:
        session.close()
