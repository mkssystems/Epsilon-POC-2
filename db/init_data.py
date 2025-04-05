import pandas as pd
from sqlalchemy.orm import sessionmaker
from models import Entity, Equipment  # Make sure the correct paths are used

def load_entities_data(session):
    # Read the entities CSV file
    df_entities = pd.read_csv('assets/seed/entities.csv')
    
    # Iterate through DataFrame and insert records into the entities table
    for _, row in df_entities.iterrows():
        entity = Entity(
            id=row['id'],
            name=row['name'],
            type=row['type'],
            age=row['age'],
            role=row['role'],
            backstory_path=row['backstory_path']
        )
        session.add(entity)
    
    session.commit()


def load_equipment_data(session):
    # Read the equipment CSV file
    df_equipment = pd.read_csv('assets/seed/equipment.csv')
    
    # Iterate through DataFrame and insert records into the equipment table
    for _, row in df_equipment.iterrows():
        equipment = Equipment(
            id=row['id'],
            entity_id=row['entity_id'],  # This links the equipment to the correct entity
            name=row['name'],
            description=row['description'] if 'description' in row else "No description available"
        )
        session.add(equipment)
    
    session.commit()


def load_data(engine):
    # Create a session
    Session = sessionmaker(bind=engine)
    session = Session()
    
    # Load data into the database
    load_entities_data(session)
    load_equipment_data(session)
