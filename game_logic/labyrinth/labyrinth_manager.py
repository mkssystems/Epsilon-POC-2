# labyrinth_manager.py

from models.labyrinth import Labyrinth
from db.session import get_session
from utils.corrected_labyrinth_backend_seed_fixed import generate_labyrinth
import uuid

class LabyrinthManager:
    """
    Explicitly manages labyrinth generation, storage, and updates.
    """

    def __init__(self, session_id: str, labyrinth_id: str):
        self.session_id = session_id
        self.labyrinth_id = labyrinth_id

    def create_labyrinth(self, seed: str, size: tuple) -> dict:
        """
        Generates a labyrinth explicitly using provided seed and size parameters.
        Stores the generated structure explicitly in the database.
        """
        labyrinth_structure = generate_labyrinth(seed, size)
        
        labyrinth_entry = Labyrinth(
            id=uuid.uuid4(),
            session_id=self.session_id,
            seed=seed,
            size=size[0],
            start_x=0,  # Explicitly placeholder values
            start_y=0,
            generated_tiles=labyrinth_structure
        )

        with get_session() as db:
            db.add(labyrinth_entry)
            db.commit()

        return labyrinth_structure

    def get_labyrinth_structure(self) -> dict:
        """
        Explicitly retrieves the current labyrinth structure from the database.
        """
        with get_session() as db:
            labyrinth = db.query(Labyrinth).filter_by(
                session_id=self.session_id,
                id=self.labyrinth_id
            ).first()

            if labyrinth:
                return labyrinth.generated_tiles
            return {}
