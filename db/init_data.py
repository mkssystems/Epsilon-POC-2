from sqlalchemy.orm import sessionmaker
from models.models import Entity, Equipment, Skill, Special

def load_data(engine, df_entities, df_equipment, df_skills, df_specials):
    Session = sessionmaker(bind=engine)
    session = Session()

    # Load entities with a safe default for 'description'
    for _, row in df_entities.iterrows():
        entity = Entity(
            name=row['name'],
            description=row.get('description', 'No description available')
        )
        session.add(entity)

    # Load equipment with a safe default for 'description'
    for _, row in df_equipment.iterrows():
        equipment = Equipment(
            entity_id=row['entity_id'],
            name=row['name'],
            description=row.get('description', 'No description available')
        )
        session.add(equipment)

    # Load skills with a safe default for 'description'
    for _, row in df_skills.iterrows():
        skill = Skill(
            entity_id=row['entity_id'],
            name=row['name'],
            description=row.get('description', 'No description available')
        )
        session.add(skill)

    # Load specials with a safe default for 'description'
    for _, row in df_specials.iterrows():
        special = Special(
            entity_id=row['entity_id'],
            name=row['name'],
            description=row.get('description', 'No description available')
        )
        session.add(special)

    session.commit()
    session.close()
