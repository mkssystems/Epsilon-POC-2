# db/init_data.py
import pandas as pd
from sqlalchemy.orm import Session
from models.game_entities import Entity  # Import Entity from game_entities
from models.equipment import Equipment  # Import Equipment from equipment
from models.skills import Skill  # Import Skill from skills
from models.specials import Special  # Import Special from specials

# Function to load data into the database
def load_data(engine, df_entities, df_equipment, df_skills, df_specials):
    # Create session for DB interaction
    session = Session(bind=engine)

    try:
        # Load entities into the 'entities' table first
        for index, row in df_entities.iterrows():
            entity = Entity(
                id=row['id'],
                name=row['name'],
                type=row['type'],
                age=row['age'],
                role=row['role'],
                backstory_path=row['backstory_path']
                portrait_path=row.get('portrait_path')  # Include portrait_path from the CSV
            )
            session.add(entity)
        
        # Commit the entities to ensure they are in the database
        session.commit()

        # Log entity IDs to debug
        print("Entities inserted:")
        for index, row in df_entities.iterrows():
            print(f"Inserted Entity ID: {row['id']}")

        # Now load equipment into the 'equipment' table
        for index, row in df_equipment.iterrows():
            # Log the entity_id before inserting equipment to debug
            print(f"Inserting Equipment with entity_id: {row['entity_id']}")
            
            # Make sure entity_id in equipment matches the id of an entity already inserted
            equipment = Equipment(
                id=row['id'],
                entity_id=row['entity_id'],  # This should match an existing entity's ID
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
