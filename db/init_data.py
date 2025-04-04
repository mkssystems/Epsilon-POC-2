import pandas as pd
from sqlalchemy.orm import Session
from db.models import Entity, Equipment, Skill, Special  # Corrected import path

def load_data(engine, df_entities, df_equipment, df_skills, df_specials):
    """
    Load data into the database ensuring correct order of insertions 
    to maintain foreign key constraints.
    """

    with Session(engine) as session:
        # Insert Entities first
        session.bulk_insert_mappings(Entity, df_entities.to_dict(orient="records"))
        session.commit()

        valid_entity_ids = set(df_entities["id"])

        # Ensure Equipment references valid Entities
        df_equipment = df_equipment[df_equipment["entity_id"].isin(valid_entity_ids)]
        session.bulk_insert_mappings(Equipment, df_equipment.to_dict(orient="records"))
        session.commit()

        # Ensure Skills reference valid Entities
        df_skills = df_skills[df_skills["entity_id"].isin(valid_entity_ids)]
        session.bulk_insert_mappings(Skill, df_skills.to_dict(orient="records"))
        session.commit()

        # Ensure Specials reference valid Entities
        df_specials = df_specials[df_specials["entity_id"].isin(valid_entity_ids)]
        session.bulk_insert_mappings(Special, df_specials.to_dict(orient="records"))
        session.commit()
