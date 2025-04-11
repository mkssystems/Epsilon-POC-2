# game_flow.py

from typing import Dict, Any
from .log_manager import LogManager
from .labyrinth.labyrinth_manager import LabyrinthManager
from .labyrinth.entity_positions import EntityPositions
from .narrative.narrative_manager import NarrativeManager
from .visuals.visual_layers_manager import VisualLayersManager
from .environment.environment_logic import EnvironmentLogic
from .actions.move import MoveAction
from .actions.fight import FightAction
from .actions.explore import ExploreAction
from .actions.stay import StayAction
from .actions.special import SpecialAction

class GameFlowManager:
    """
    Explicitly manages the overall flow of the game, including initialization,
    turn sequencing, action resolution, environmental effects, and scenario conclusion.
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
        self.environment_logic = EnvironmentLogic(session_id)

    def initialize_game(self, scenario_id: str, seed: str, size: tuple, entities_initial_positions: Dict[str, Any]) -> None:
        labyrinth_structure = self.labyrinth_manager.create_labyrinth(seed, size)
        for entity_id, entity_data in entities_initial_positions.items():
            tile_id = entity_data["initial_tile_id"]
            entity_type = entity_data["entity_type"]
            self.entity_positions.track_entity_position(self.turn_number, entity_id, entity_type, tile_id)

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

        event_details = self.environment_logic.generate_environmental_event()
        self.environment_logic.apply_event_effects(event_details)

        self.logger.create_log_entry(
            turn_number=self.turn_number,
            actor_type="environment",
            actor_id="system",
            action_phase="environment",
            action_type=event_details["event_type"],
            description=event_details["effect"]["effect_description"],
            additional_data=event_details["effect"]
        )

        print(f"Starting turn {self.turn_number} for session {self.session_id}")

    def resolve_turn_actions(self, actions_to_resolve: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        results = {}
        for entity_id, action_info in actions_to_resolve.items():
            action_type = action_info["action_type"]
            params = action_info["params"]

            if action_type == "Move":
                action = MoveAction(entity_id, params)
            elif action_type == "Fight":
                action = FightAction(entity_id, params)
            elif action_type == "Explore":
                action = ExploreAction(entity_id, params)
            elif action_type == "Stay":
                action = StayAction(entity_id, params)
            elif action_type == "Special":
                action = SpecialAction(entity_id, params)
            else:
                continue  # Unknown action type

            result = action.execute()
            narrative = action.generate_narrative()

            self.logger.create_log_entry(
                turn_number=self.turn_number,
                actor_type="entity",
                actor_id=entity_id,
                action_phase="resolution",
                action_type=action_type,
                description=narrative,
                additional_data=result
            )

            results[entity_id] = {"result": result, "narrative": narrative}

        print(f"Actions resolved explicitly for turn {self.turn_number}: {results}")
        return results

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
