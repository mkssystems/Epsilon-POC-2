from sqlalchemy.orm import sessionmaker
from models.models import Entity, Equipment, Skill, Special

def load_data(engine, df_entities, df_equipment, df_skills, df_specials):
    Session = sessionmaker(bind=engine)
    session = Session()

    for _, row in df_entities.iterrows():
        entity = Entity(
            name=row.get('name', 'Unnamed Entity'),
            description=row.get('description', 'No description available')
        )
        session.add(entity)

    for _, row in df_equipment.iterrows():
        equipment = Equipment(
            entity_id=row.get('entity_id'),
            name=row.get('name', 'Unnamed Equipment'),
            description=row.get('description', 'No description available')
        )
        session.add(equipment)

    for _, row in df_skills.iterrows():
        skill = Skill(
            entity_id=row.get('entity_id'),
            name=row.get('name', 'Unnamed Skill'),
            description=row.get('description', 'No description available')
        )
        session.add(skill)

    for _, row in df_specials.iterrows():
        special = Special(
            entity_id=row.get('entity_id'),
            name=row.get('name', 'Unnamed Special'),
            description=row.get('description', 'No description available')
        )
        session.add(special)

    session.commit()
    session.close()
