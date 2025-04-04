import pandas as pd
from sqlalchemy.orm import sessionmaker
from models.game_entities import Entity, Equipment, Skill, Special

# Function to load data into the database
def load_data(engine, df_entities: pd.DataFrame, df_equipment: pd.DataFrame, df_skills: pd.DataFrame, df_specials: pd.DataFrame):
    Session = sessionmaker(bind=engine)
    session = Session()

    try:
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
    finally:
        session.close()

