# game_flow.py

from typing import Dict, Any
from .log_manager import LogManager
from .labyrinth.labyrinth_manager import LabyrinthManager
from .labyrinth.entity_positions import EntityPositions
from .narrative.narrative_manager import NarrativeManager
from .visuals.visual_layers_manager import VisualLayersManager

class GameFlowManager:
    """
    Explicitly manages the overall flow of the game, including initialization,
    turn sequencing, action resolution, and scenario conclusion.
    """

    def __init__(self, session_id: str, labyrinth_id: str):
        self.session_id = session_id
        self.labyrinth_id = labyrinth_id
        self.turn_number = 0
        self.logger = LogManager(session_id)
        self.labyrinth_manager = LabyrinthManager(session_id, labyrinth_id)
        self.entity_positions = EntityPositions(session_id, labyrinth_id)
        self.narrative_manager = NarrativeManager(session_id)
        self.visual_layers_manager = VisualLayersManager(session_id)

    def initialize_game(self, scenario_id: str, seed: str, size: tuple, entities_initial_positions: Dict[str, Any]) -> None:
        labyrinth_structure = self.labyrinth_manager.create_labyrinth(seed, size)
        for entity_id, entity_data in entities_initial_positions.items():
            tile_id = entity_data["initial_tile_id"]
            entity_type = entity_data["entity_type"]
            self.entity_positions.track_entity_position(self.turn_number, entity_id, entity_type, tile_id)

        initial_narrative = self.narrative_manager.generate_tile_narrative(tile_id, entity_id)
        initial_visual = self.visual_layers_manager.generate_visual_layers(tile_id, [], [])

        self.logger.create_log_entry(
            turn_number=self.turn_number,
            actor_type="backend",
            actor_id="system",
            action_phase="initialization",
            action_type="Setup",
            description=f"Game initialized for scenario {scenario_id}",
            additional_data={"labyrinth_structure": labyrinth_structure}
        )

        print(f"Game session {self.session_id} initialized explicitly for scenario {scenario_id}.")
        print(f"Initial Narrative: {initial_narrative}")
        print(f"Initial Visual Layers: {initial_visual}")

    def start_next_turn(self) -> None:
        self.turn_number += 1
        self.logger.create_log_entry(
            turn_number=self.turn_number,
            actor_type="backend",
            actor_id="system",
            action_phase="turn_start",
            action_type="StartTurn",
            description=f"Starting turn {self.turn_number}"
        )
        print(f"Starting turn {self.turn_number} for session {self.session_id}")

    def resolve_turn_actions(self) -> Dict[str, Any]:
        self.logger.create_log_entry(
            turn_number=self.turn_number,
            actor_type="backend",
            actor_id="system",
            action_phase="resolution",
            action_type="ResolveActions",
            description=f"Resolving actions for turn {self.turn_number}"
        )
        print(f"Resolving actions for turn {self.turn_number}")
        # Placeholder logic for action resolution
        return {"result": "Action resolution explicitly pending implementation."}

    def generate_turn_narrative_and_visuals(self, tile_id: str, entity_id: str) -> Dict[str, Any]:
        narrative = self.narrative_manager.generate_tile_narrative(tile_id, entity_id)
        visuals = self.visual_layers_manager.generate_visual_layers(tile_id, [], [])
        
        print(f"Generated narrative explicitly for turn {self.turn_number}: {narrative}")
        print(f"Generated visual layers explicitly for turn {self.turn_number}: {visuals}")
        
        return {"narrative": narrative, "visual_layers": visuals}

    def check_end_conditions(self) -> bool:
        end_conditions_met = False  # Placeholder logic
        self.logger.create_log_entry(
            turn_number=self.turn_number,
            actor_type="backend",
            actor_id="system",
            action_phase="evaluation",
            action_type="CheckEndConditions",
            description=f"End conditions met: {end_conditions_met}"
        )
        print(f"Checking end conditions for turn {self.turn_number}")
        return end_conditions_met

    def conclude_game(self) -> Dict[str, Any]:
        self.logger.create_log_entry(
            turn_number=self.turn_number,
            actor_type="backend",
            actor_id="system",
            action_phase="conclusion",
            action_type="ConcludeGame",
            description=f"Concluding game session {self.session_id}"
        )
        print(f"Concluding game session {self.session_id}")
        return {"outcome": "Game conclusion logic explicitly pending implementation."}
