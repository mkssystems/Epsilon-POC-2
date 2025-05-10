# game_logic/phases/turn_zero.py
from datetime import datetime
from game_logic.data.game_state import (
    GamePhaseName, TurnInfo, PhaseInfo, GameState, GameInfo, Tile, TileEntity, EntityDetail
)
from utils.db_utils import save_game_state_to_db
from realtime import broadcast_session_update
import asyncio
from models.game_session import GameSession
from models.tile import Tile as DbTile
from game_logic.scenarios.epsilon267_fulcrum_incident.epsilon267_fulcrum_incident_entities_placement import (
    place_players, place_enemies, place_npcs
)
from game_logic.scenarios.epsilon267_fulcrum_incident.map_objects_placement import place_map_objects
from models.game_entities import Entity as DbEntity
from models.session_player_character import SessionPlayerCharacter  # Explicitly import model
from game_logic.scenarios.epsilon267_fulcrum_incident.thematic_overlay import apply_thematic_overlay  # Explicit import for thematic overlay logic


# Explicitly retrieve scenario details from the database
def retrieve_scenario_details(db_session, session_id):
    session = db_session.query(GameSession).filter(GameSession.id == session_id).first()
    if session:
        return session.scenario_name, session.labyrinth_id, session.size, session.seed
    raise ValueError(f"No game session found with id {session_id}")

# Explicitly broadcast game start event asynchronously
def broadcast_game_started(session_id, scenario_name):
    message = {"event": "game_started", "scenario_name": scenario_name}
    asyncio.create_task(broadcast_session_update(session_id, message))

# Explicitly define the initial labyrinth with entities and map objects
def define_initial_labyrinth(db_session, labyrinth_id, entities_positions, map_objects_positions):
    tile_records = db_session.query(DbTile).filter(DbTile.labyrinth_id == labyrinth_id).all()
    if not tile_records:
        error_msg = f"No tiles found explicitly for labyrinth_id={labyrinth_id}"
        print(f"[ERROR] {error_msg}")
        raise ValueError(error_msg)

    labyrinth = {}
    for tile_record in tile_records:
        tile_id_str = str(tile_record.id)
        labyrinth[tile_id_str] = Tile(
            x=tile_record.x,
            y=tile_record.y,
            type=tile_record.type,
            revealed=False,
            open_directions=tile_record.open_directions,
            effect_keyword=None,
            entities=[
                TileEntity(id=entity_id, type=db_session.query(DbEntity).filter(DbEntity.id == entity_id).first().type)
                for entity_id, position in entities_positions.items()
                if position == tile_id_str
            ],
            map_object=map_objects_positions.get(tile_id_str)
        )
    print(f"[INFO] Labyrinth initialized explicitly with {len(tile_records)} tiles")
    return labyrinth

# Explicitly define initial entity details
def define_initial_entity_details(db_session, entities_positions, player_entities_with_clients):
    entities = {}

    # Explicitly build a dictionary mapping entity IDs to client IDs for quick lookup
    client_controlled_entities = {entity.id: client_id for entity, client_id in player_entities_with_clients}

    for entity_id in entities_positions:
        db_entity = db_session.query(DbEntity).filter(DbEntity.id == entity_id).first()
        if not db_entity:
            error_msg = f"No entity record found explicitly for entity_id={entity_id}"
            print(f"[ERROR] {error_msg}")
            raise ValueError(error_msg)

        # Explicitly set controlled_by_user_id for player entities; otherwise None
        entities[entity_id] = EntityDetail(
            type=db_entity.type,
            controlled_by_user_id=client_controlled_entities.get(entity_id)
        )

    # Log explicitly the initialized entities and their controllers
    print(f"[INFO] Explicitly initialized entity details with user control associations: "
          f"{[(eid, detail.controlled_by_user_id) for eid, detail in entities.items()]}")
    
    return entities


# Main procedural orchestrating function for Turn 0 initialization
def execute_turn_zero(db_session, session_id):
    # Explicitly ensure correct parameter passing here
    try:
        scenario_name, labyrinth_id, size, seed = retrieve_scenario_details(db_session, session_id)
        print(f"[INFO] Scenario details retrieved successfully: Scenario='{scenario_name}', Labyrinth='{labyrinth_id}', Size={size}, Seed='{seed}'")
    except Exception as e:
        print(f"[ERROR] Failed to retrieve scenario details: {e}")
        raise

    broadcast_game_started(session_id, scenario_name)

    turn_info = TurnInfo(number=0, started_at=datetime.utcnow())
    phase_info = PhaseInfo(
        name=GamePhaseName.TURN_0,
        number=None,
        is_end_turn=False,
        started_at=datetime.utcnow()
    )
    print(f"[INFO] Turn and phase explicitly initialized: {turn_info}, {phase_info}")

    try:
        # Explicitly retrieve only selected player characters for this session
        chosen_characters = db_session.query(SessionPlayerCharacter).filter(
            SessionPlayerCharacter.session_id == session_id
        ).all()
        
        # Check explicitly if any player has selected a character for this session
        if not chosen_characters:
            error_msg = f"No player characters explicitly chosen for session {session_id}"
            print(f"[ERROR] {error_msg}")
            raise ValueError(error_msg)
        
        # Explicitly fetch entities and associate them with the controlling client IDs
        player_entities_with_clients = []
        for choice in chosen_characters:
            entity = db_session.query(DbEntity).filter(DbEntity.id == choice.entity_id).first()
            if not entity:
                error_msg = f"Explicitly selected entity_id={choice.entity_id} not found in DbEntity"
                print(f"[ERROR] {error_msg}")
                raise ValueError(error_msg)
            player_entities_with_clients.append((entity, choice.client_id))
        
        # Log explicitly retrieved players and associated clients for tracking
        print(f"[INFO] Explicitly retrieved player entities and their controlling clients: "
              f"{[(entity.id, client_id) for entity, client_id in player_entities_with_clients]}")
        
        # Explicitly place only chosen player entities
        player_positions, player_tile = place_players(
            db_session, session_id, [entity for entity, _ in player_entities_with_clients]
        )
        print(f"[INFO] Players explicitly positioned at: {player_positions}")
        
        # Continue explicitly retrieving enemy and NPC entities as before (no changes here)
        enemy_entities = db_session.query(DbEntity).filter(
            DbEntity.scenario == scenario_name, DbEntity.type == "enemy"
        ).all()
        npc_entities = db_session.query(DbEntity).filter(
            DbEntity.scenario == scenario_name, DbEntity.type == "npc"
        ).all()


        enemy_positions, boss_tile = place_enemies(db_session, session_id, enemy_entities, player_tile)
        print(f"[INFO] Enemies positioned: {enemy_positions}")

        npc_positions = place_npcs(db_session, session_id, npc_entities, boss_tile)
        print(f"[INFO] NPCs positioned: {npc_positions}")

        entities_positions = {**player_positions, **enemy_positions, **npc_positions}
        map_objects_positions = place_map_objects(db_session, session_id, scenario_name)
        print(f"[INFO] Map objects positioned: {map_objects_positions}")

        # Explicitly apply thematic overlay logic to tile records before initializing labyrinth
        tile_records = db_session.query(DbTile).filter(DbTile.labyrinth_id == labyrinth_id).all()
        apply_thematic_overlay(tile_records)  # Assign thematic area and tile codes explicitly
        db_session.commit()  # Explicitly save thematic assignments to DB
    
    except Exception as e:
        print(f"[ERROR] Entity or map object placement or thematic overlay failed: {e}")
        raise

    labyrinth = define_initial_labyrinth(db_session, labyrinth_id, entities_positions, map_objects_positions)
    entities = define_initial_entity_details(db_session, entities_positions, player_entities_with_clients)

    game_state = GameState(
        game_info=GameInfo(
            session_id=session_id,
            scenario=scenario_name,
            labyrinth_id=str(labyrinth_id),
            size=size,
            seed=seed
        ),
        turn=turn_info,
        phase=phase_info,
        labyrinth=labyrinth,
        entities=entities
    )
    
    # Explicitly serialize the game state
    game_state_dict = game_state.to_json()
    
    try:
        save_game_state_to_db(db_session, game_state)
        print(f"[INFO] Game state explicitly saved successfully.")
    except Exception as e:
        print(f"[ERROR] Game state saving failed explicitly: {e}")
        raise
    
    # Explicitly broadcast the correct, serialized game state
    asyncio.create_task(broadcast_session_update(session_id, {
        "event": "game_state_initialized",
        "game_state": game_state_dict
    }))
    
    print(f"[INFO] Turn 0 explicitly initialized and broadcasted for session '{session_id}'")
