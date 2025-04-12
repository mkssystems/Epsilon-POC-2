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
from .entities.npc_logic import NPC
from .entities.enemy_logic import Enemy
from .utils.timers import ActionTimer
from .utils.state_sync import StateSyncManager

class GameFlowManager:
    """
    Explicitly manages the overall flow of the game, including initialization,
    turn sequencing, action resolution, environmental effects, player inactivity,
    reconnections, and scenario conclusion.
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
        self.npcs = {}
        self.enemies = {}
        self.timers = {}
        self.state_sync_manager = StateSyncManager(session_id)

    def start_player_inactivity_timer(self, player_id: str, timeout_seconds: int):
        """
        Explicitly starts inactivity timer for a player.
        """
        timer = ActionTimer(timeout_seconds, self.apply_default_player_action, player_id)
        timer.start_timer()
        self.timers[player_id] = timer
        print(f"Inactivity timer explicitly started for player '{player_id}'.")

    def cancel_player_inactivity_timer(self, player_id: str):
        """
        Explicitly cancels inactivity timer when player acts.
        """
        if player_id in self.timers:
            self.timers[player_id].cancel_timer()
            del self.timers[player_id]
            print(f"Inactivity timer explicitly cancelled for player '{player_id}'.")

    def apply_default_player_action(self, player_id: str):
        """
        Explicitly applies the default 'Stay' action upon player inactivity.
        """
        action = StayAction(player_id)
        result = action.execute()
        narrative = action.generate_narrative()
        self.logger.create_log_entry(
            turn_number=self.turn_number,
            actor_type="player",
            actor_id=player_id,
            action_phase="resolution",
            action_type="Stay",
            description=narrative,
            additional_data=result
        )
        print(f"Default action explicitly applied for inactive player '{player_id}'.")

    def handle_player_reconnection(self, player_id: str) -> Dict[str, Any]:
        """
        Explicitly handles player reconnection and provides game state synchronization.
        """
        state_data = self.state_sync_manager.synchronize_state(player_id)
        self.logger.create_log_entry(
            turn_number=self.turn_number,
            actor_type="player",
            actor_id=player_id,
            action_phase="reconnection",
            action_type="StateSync",
            description=f"Player '{player_id}' reconnected and synchronized.",
            additional_data=state_data
        )
        print(f"Player '{player_id}' explicitly reconnected and synchronized.")
        return state_data

   

    def initialize_game(self, scenario_id: str, seed: str, size: tuple, entities_initial_positions: Dict[str, Any]) -> None:
        labyrinth_structure = self.labyrinth_manager.create_labyrinth(seed, size)
        for entity_id, entity_data in entities_initial_positions.items():
            tile_id = entity_data["initial_tile_id"]
            entity_type = entity_data["entity_type"]
            self.entity_positions.track_entity_position(self.turn_number, entity_id, entity_type, tile_id)

            if entity_type == "NPC":
                self.npcs[entity_id] = NPC(entity_id, entity_data["name"], tile_id)
            elif entity_type == "Enemy":
                self.enemies[entity_id] = Enemy(entity_id, entity_data["name"], tile_id)

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

    def collect_entity_actions(self, player_positions: Dict[str, str]) -> Dict[str, Any]:
        actions_to_resolve = {}

        for npc_id, npc in self.npcs.items():
            action_decision = npc.decide_next_action()
            actions_to_resolve[npc_id] = action_decision

        for enemy_id, enemy in self.enemies.items():
            action_decision = enemy.decide_next_action(player_positions)
            actions_to_resolve[enemy_id] = action_decision

        print(f"Collected entity actions explicitly for turn {self.turn_number}: {actions_to_resolve}")
        return actions_to_resolve

    def resolve_turn_actions(self, actions_to_resolve: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        results = {}
        for entity_id, action_info in actions_to_resolve.items():
            action_type = action_info["action"]
            params = action_info.get("params", {})

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

    def confirm_game_start(session_id):
        # Check session existence
        session = scenario_manager.get_game_session(session_id)
        if not session:
            log_manager.log_event(session_id, None, "GameStart", "validation",
                                  "Game session validation failed - session not found.")
            raise Exception("Game session not found. Cannot start the game.")
    
        # Check labyrinth existence
        labyrinth = labyrinth_manager.get_existing_labyrinth(session.labyrinth_id)
        if not labyrinth:
            log_manager.log_event(session_id, None, "GameStart", "validation",
                                  "Labyrinth validation failed - labyrinth structure not found.")
            raise Exception("Labyrinth not found or improperly configured.")
    
        # Confirm session readiness (e.g., state should be 'lobby_ready')
        if session.state != "lobby_ready":
            log_manager.log_event(session_id, None, "GameStart", "validation",
                                  f"Invalid session state: {session.state}")
            raise Exception(f"Session state invalid: {session.state}")
    
        # All checks explicitly passed
        log_manager.log_event(session_id, None, "GameStart", "validation",
                              "Existing session and labyrinth validated successfully.")
        return session, labyrinth

