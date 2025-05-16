# routes/api.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from models.game_session import GameSession
from models.mobile_client import MobileClient
from uuid import UUID, uuid4
from datetime import datetime
from schemas import ClientJoinRequest, GameSessionCreateRequest, PlayerStatus, SessionStatus
from utils.corrected_labyrinth_backend_seed_fixed import generate_labyrinth, get_image_filename
from realtime import broadcast_session_update
from realtime import broadcast_game_started
from models import Entity, SessionPlayerCharacter
from realtime import broadcast_character_selected
from realtime import broadcast_character_released
from game_logic.models.game_state_db import GameStateDB
from db.session import get_db  # Your existing DB session handler explicitly
from game_logic.game_flow_controller import GameFlowController
from models.tile import Tile
from game_logic.data.game_state import GamePhaseName, PhaseInfo, TurnInfo
from datetime import datetime
from utils.db_utils import load_initial_game_state, save_game_state_to_db
from game_logic.game_flow_controller import GameFlowController
import json  # explicitly import json




router = APIRouter()

@router.post("/game_sessions/{session_id}/start_game")
async def start_game(session_id: str, db: Session = Depends(get_db)):
    # Explicitly load the current game state from DB
    game_state = load_initial_game_state(db, session_id)

    # Explicitly update phase and turn to TURN_0 if currently WAITING_FOR_PLAYERS
    if game_state.phase.name == GamePhaseName.WAITING_FOR_PLAYERS:
        current_time = datetime.utcnow()
        
        game_state.phase = PhaseInfo(
            name=GamePhaseName.TURN_0,
            number=0,
            is_end_turn=False,
            started_at=current_time
        )
        
        game_state.turn = TurnInfo(
            number=0,
            started_at=current_time
        )

        # Explicitly save updated game state to DB
        save_game_state_to_db(db, game_state)

    # Explicitly invoke GameFlowController after state update
    controller = GameFlowController(session_id)
    controller.start_game()

    # Explicitly reset readiness after starting the game
    db.query(MobileClient).filter(
        MobileClient.game_session_id == session_id
    ).update({"is_ready": False})

    db.commit()

    # Explicitly broadcast new readiness status
    all_clients = db.query(MobileClient).filter(
        MobileClient.game_session_id == session_id
    ).all()

    players = [
        PlayerStatus(client_id=client.client_id, ready=client.is_ready)
        for client in all_clients
    ]

    session_status = SessionStatus(players=players, all_ready=False)
    await broadcast_session_update(session_id, session_status.dict())

    return {"message": "Game explicitly started successfully"}


@router.get('/game_sessions')
async def get_game_sessions(db: Session = Depends(get_db)):
    sessions = db.query(GameSession).all()
    return {"sessions": sessions}

@router.post('/game_sessions/{session_id}/join')
async def join_game_session(session_id: UUID, request: ClientJoinRequest, db: Session = Depends(get_db)):
    session = db.query(GameSession).filter(GameSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail='Session not found')

    existing_client = db.query(MobileClient).filter(
        MobileClient.client_id == request.client_id,
        MobileClient.game_session_id == session_id
    ).first()

    if existing_client:
        print(f"[INFO] Explicit log: Client already connected: client_id={request.client_id}, session_id={session_id}")
        return {'message': 'Client already connected'}

    # Explicitly create new client entry with readiness set to False by default
    new_client = MobileClient(
        client_id=request.client_id,
        game_session_id=session.id,
        connected_at=datetime.utcnow(),
        is_ready=False
    )

    db.add(new_client)
    db.commit()
    db.refresh(new_client)

    # Explicit debug logging confirming successful join
    print(f"[INFO] Client explicitly added: client_id={request.client_id}, session_id={session_id}")

    # Explicitly retrieve readiness status of all connected clients from DB
    all_clients = db.query(MobileClient).filter(MobileClient.game_session_id == session_id).all()

    players = [
        PlayerStatus(client_id=client.client_id, ready=client.is_ready)
        for client in all_clients
    ]

    all_ready = all(client.is_ready for client in all_clients)

    session_status = SessionStatus(players=players, all_ready=all_ready)

    # Explicitly broadcast current DB-driven readiness state
    await broadcast_session_update(str(session_id), session_status.dict())

    return {
        'message': 'Connected successfully',
        'session_id': str(session.id),
        'map_seed': session.seed,
        'labyrinth_id': str(session.labyrinth_id),
        'size': session.size,
        'creator_client_id': session.creator_client_id,
        'scenario_name': session.scenario_name,
        'difficulty': session.difficulty,
        'max_players': session.max_players,
        'created_at': session.created_at.isoformat()
    }



@router.get('/game_sessions/{session_id}/clients')
async def get_connected_clients(session_id: UUID, db: Session = Depends(get_db)):
    session = db.query(GameSession).filter(GameSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail='Session not found')

    return {
        'clients': [
            {
                'client_id': client.client_id,
                'connected_at': client.connected_at.isoformat()
            } for client in session.connected_clients
        ]
    }

@router.post('/game_sessions/create')
async def create_game_session(request: GameSessionCreateRequest, db: Session = Depends(get_db)):
    labyrinth, _ = generate_labyrinth(request.size, None, db)

    new_session = GameSession(
        id=uuid4(),
        seed=labyrinth.seed,
        labyrinth_id=labyrinth.id,
        size=request.size,
        creator_client_id=request.creator_client_id,
        scenario_name=request.scenario_name,
        difficulty=request.difficulty,
        max_players=request.max_players,
        created_at=datetime.utcnow()
    )
    db.add(new_session)
    db.commit()
    db.refresh(new_session)

    # Explicitly create initial game state
    initial_game_state = {
        "game_info": {
            "session_id": str(new_session.id),
            "scenario": request.scenario_name,
            "labyrinth_id": str(labyrinth.id),
            "size": request.size,
            "seed": labyrinth.seed
        },
        "turn": {
            "number": -1,
            "started_at": None
        },
        "phase": {
            "name": "WAITING_FOR_PLAYERS",
            "number": None,
            "is_end_turn": False,
            "started_at": None
        },
        "labyrinth": {},
        "entities": {}
    }

    # Explicitly insert the initial state into the GameStateDB
    new_game_state_db = GameStateDB(
        session_id=str(new_session.id),
        game_state=initial_game_state
    )
    db.add(new_game_state_db)
    db.commit()

    return {
        'message': 'Game session created successfully',
        'session_id': str(new_session.id),
        'seed': new_session.seed,
        'labyrinth_id': str(new_session.labyrinth_id),
        'size': new_session.size,
        'creator_client_id': new_session.creator_client_id,
        'scenario_name': new_session.scenario_name,
        'difficulty': new_session.difficulty,
        'max_players': new_session.max_players
    }


@router.post('/game_sessions/leave')
async def leave_game_session(request: ClientJoinRequest, db: Session = Depends(get_db)):
    # Explicitly fetch client to be removed
    existing_client = db.query(MobileClient).filter(
        MobileClient.client_id == request.client_id
    ).first()

    if not existing_client:
        raise HTTPException(status_code=404, detail='Client not connected to any session')

    session_id = existing_client.game_session_id

    # Explicitly remove client from DB
    db.delete(existing_client)
    db.commit()

    # Explicitly fetch remaining connected clients from DB
    remaining_clients = db.query(MobileClient).filter(
        MobileClient.game_session_id == session_id
    ).all()

    # Construct readiness status explicitly from DB data
    players = [
        PlayerStatus(client_id=client.client_id, ready=client.is_ready)
        for client in remaining_clients
    ]

    # Explicitly calculate overall readiness state
    all_ready = all(player.ready for player in players) if players else False

    session_status = SessionStatus(players=players, all_ready=all_ready)

    # Broadcast explicitly constructed DB-based state via WebSocket
    await broadcast_session_update(str(session_id), session_status.dict())

    return {'message': 'Disconnected successfully'}


@router.get("/game_sessions/client_state/{client_id}")
async def get_client_state(client_id: str, db: Session = Depends(get_db)):
    client = db.query(MobileClient).filter(MobileClient.client_id == client_id).first()
    if client and client.game_session_id:
        session = db.query(GameSession).filter(GameSession.id == client.game_session_id).first()
        if session:
            return {
                "client_id": client_id,
                "connected_session": str(session.id),
                "session_details": {
                    "session_id": str(session.id),
                    "labyrinth_id": str(session.labyrinth_id),
                    "seed": session.seed,
                    "size": session.size,
                    "creator_client_id": session.creator_client_id,
                    "scenario_name": session.scenario_name,
                    "difficulty": session.difficulty,
                    "max_players": session.max_players,
                    "created_at": session.created_at.isoformat()
                }
            }
    return {"client_id": client_id, "connected_session": None, "session_details": None}

@router.post("/game_sessions/{session_id}/toggle_readiness", response_model=SessionStatus)
async def toggle_readiness(session_id: UUID, payload: PlayerStatus, db: Session = Depends(get_db)):
    # Explicitly verify client exists and is part of session
    client = db.query(MobileClient).filter(
        MobileClient.client_id == payload.client_id,
        MobileClient.game_session_id == session_id
    ).first()

    if not client:
        raise HTTPException(status_code=404, detail="Client not found in session.")

    # Explicitly verify character selection if setting ready
    selection = db.query(SessionPlayerCharacter).filter_by(
        session_id=session_id, client_id=payload.client_id
    ).first()

    if payload.ready and not selection:
        raise HTTPException(status_code=400, detail="Character must be selected before ready.")

    # Update readiness explicitly in DB
    client.is_ready = payload.ready

    # Explicitly update character lock state if selection exists
    if selection:
        selection.locked = payload.ready

    db.commit()

    # Fetch updated readiness explicitly from DB
    all_clients = db.query(MobileClient).filter(
        MobileClient.game_session_id == session_id
    ).all()

    players = [
        PlayerStatus(client_id=client.client_id, ready=client.is_ready)
        for client in all_clients
    ]

    all_ready = all(client.is_ready for client in all_clients)

    session_status = SessionStatus(players=players, all_ready=all_ready)

    # Explicitly broadcast DB-driven readiness via WebSocket
    await broadcast_session_update(str(session_id), session_status.dict())

    return session_status




@router.get("/game_sessions/{session_id}/status", response_model=SessionStatus)
async def get_session_status(session_id: UUID, db: Session = Depends(get_db)):
    # Explicitly fetch all connected clients and their readiness status from the database
    clients = db.query(MobileClient).filter(
        MobileClient.game_session_id == session_id
    ).all()

    # Construct player statuses directly from DB entries
    players = [
        PlayerStatus(client_id=client.client_id, ready=client.is_ready)
        for client in clients
    ]

    # Explicitly calculate if all connected players are ready
    all_ready = all(player.ready for player in players) if players else False

    # Explicitly return session status constructed purely from DB state
    return SessionStatus(players=players, all_ready=all_ready)


@router.delete('/game_sessions/destroy_all')
async def destroy_all_sessions(db: Session = Depends(get_db)):
    try:
        db.query(MobileClient).delete()  # Delete connected mobile clients first to avoid foreign key constraints
        db.query(GameSession).delete()
        db.commit()
        return {"message": "All sessions destroyed successfully"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.get('/game_sessions/user/{client_id}')
async def get_user_game_sessions(client_id: str, db: Session = Depends(get_db)):
    sessions = db.query(GameSession).filter(GameSession.creator_client_id == client_id).all()
    return {"sessions": sessions}

@router.get('/game_sessions/user/{client_id}/joined')
async def get_joined_game_sessions(client_id: str, db: Session = Depends(get_db)):
    sessions = db.query(GameSession).join(MobileClient).filter(
        MobileClient.client_id == client_id,
        GameSession.creator_client_id != client_id
    ).all()

    return {"sessions": sessions}

# Explicitly fetch characters that are not yet selected by any player (locked OR unlocked)
@router.get("/game_sessions/{session_id}/available_characters")
async def available_characters(session_id: UUID, db: Session = Depends(get_db)):
    # Fetch the game session explicitly
    session = db.query(GameSession).filter(GameSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    # Explicitly get IDs of ALL selected characters (regardless of locked status!)
    chosen_characters = db.query(SessionPlayerCharacter).filter(
        SessionPlayerCharacter.session_id == session_id
    ).with_entities(SessionPlayerCharacter.entity_id).all()

    chosen_character_ids = [char.entity_id for char in chosen_characters]

    # Explicitly exclude all currently selected characters from availability
    characters = db.query(Entity).filter(
        Entity.type == 'player',
        Entity.scenario == session.scenario_name,
        ~Entity.id.in_(chosen_character_ids)  # Explicit exclusion of all selected characters
    ).all()

    return {"available_characters": characters}



# Endpoint for a player to select a character in a specific session
@router.post("/game_sessions/{session_id}/select_character")
async def select_character(session_id: UUID, client_id: str, entity_id: str, db: Session = Depends(get_db)):
    # Check if the desired character is already selected by another player (locked or unlocked)
    existing_selection_by_others = db.query(SessionPlayerCharacter).filter(
        SessionPlayerCharacter.session_id == session_id,
        SessionPlayerCharacter.entity_id == entity_id,
        SessionPlayerCharacter.client_id != client_id
    ).first()

    if existing_selection_by_others:
        raise HTTPException(
            status_code=400,
            detail="Character already selected by another player."
        )

    # Fetch existing selection explicitly for the current client (if any)
    existing_selection = db.query(SessionPlayerCharacter).filter_by(
        session_id=session_id,
        client_id=client_id
    ).first()

    if existing_selection:
        # Ensure player is not locked (ready); locked players can't change their character
        if existing_selection.locked:
            raise HTTPException(
                status_code=400,
                detail="Cannot change character when ready. Please toggle readiness first."
            )
        # Explicitly update the character selection for the current player
        existing_selection.entity_id = entity_id
    else:
        # Explicitly create new character selection if none exists
        existing_selection = SessionPlayerCharacter(
            session_id=session_id,
            client_id=client_id,
            entity_id=entity_id,
            locked=False
        )
        db.add(existing_selection)

    db.commit()

    # Notify all connected clients explicitly about this character selection
    await broadcast_character_selected(str(session_id), client_id, entity_id)

    return {"message": "Character selected successfully."}


@router.post("/game_sessions/{session_id}/release_character")
async def release_character(session_id: UUID, client_id: str, db: Session = Depends(get_db)):
    # Explicitly fetch existing selection for this player only
    selection = db.query(SessionPlayerCharacter).filter_by(
        session_id=session_id, client_id=client_id
    ).first()

    # Handle explicitly if no character is currently selected by this player
    if not selection:
        raise HTTPException(status_code=400, detail="No character selected to release.")

    # Explicitly prevent releasing the character if player is ready (locked)
    if selection.locked:
        raise HTTPException(
            status_code=400,
            detail="Cannot release character when ready. Please toggle readiness first."
        )

    entity_id = selection.entity_id

    # Explicitly delete only this player's selection without affecting others
    db.delete(selection)
    db.commit()

    # Explicitly broadcast character released event only for this player's selection
    await broadcast_character_released(str(session_id), client_id, entity_id)

    return {"message": "Character released successfully."}



# Endpoint to fetch currently selected characters for all clients connected to a specific game session
@router.get("/game_sessions/{session_id}/selected_characters")
async def get_selected_characters(session_id: UUID, db: Session = Depends(get_db)):
    session = db.query(GameSession).filter(GameSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    connected_clients = session.connected_clients

    selected_characters = []

    for client in connected_clients:
        selection = db.query(SessionPlayerCharacter).filter_by(
            session_id=session_id,
            client_id=client.client_id
        ).first()

        selected_characters.append({
            "client_id": client.client_id,
            # Explicitly set to None if no selection is present
            "entity_id": selection.entity_id if selection else None,
            "locked": selection.locked if selection else False
        })

    return {"selected_characters": selected_characters}


# Explicitly fetch ALL scenario characters (including selected and locked ones)
@router.get("/game_sessions/{session_id}/all_characters")
async def all_characters(session_id: UUID, db: Session = Depends(get_db)):
    session = db.query(GameSession).filter(GameSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    # Explicitly fetch ALL player characters for the scenario
    characters = db.query(Entity).filter(
        Entity.type == 'player',
        Entity.scenario == session.scenario_name
    ).all()

    return {"all_characters": characters}

@router.get('/game-state/{session_id}')
async def get_full_game_state(session_id: UUID, db: Session = Depends(get_db)):
    """
    Retrieve and explicitly return the full game state for a given session ID.

    Args:
        session_id (UUID): Unique identifier for the game session.
        db (Session): Database session dependency injected by FastAPI.

    Returns:
        dict: Full serialized game state including labyrinth details,
              entities positions, and map objects.
              
    Raises:
        HTTPException: 404 if the game state for provided session ID is not found.
    """
    try:
        # Explicitly convert UUID to string for consistent DB querying
        session_id_str = str(session_id)

        # Explicitly query GameStateDB for the provided session_id
        game_state_entry = db.query(GameStateDB).filter(
            GameStateDB.session_id == session_id_str
        ).first()

        # Explicitly handle the case where no game state is found
        if not game_state_entry:
            raise HTTPException(
                status_code=404,
                detail=f"Game state for session '{session_id_str}' not found."
            )

        # Explicitly return the game state as a parsed JSON
        return game_state_entry.game_state

    except Exception as e:
        # Explicitly handle unexpected exceptions gracefully
        raise HTTPException(
            status_code=500,
            detail=f"An unexpected error occurred: {str(e)}"
        )

# API endpoint to retrieve a detailed visual representation of the labyrinth map for frontend visualization
@router.get('/game-state/{session_id}/visual-map')
async def get_visual_map(session_id: UUID, db: Session = Depends(get_db)):
    # Explicitly convert UUID to string for consistent database querying
    session_id_str = str(session_id)

    # Retrieve the game state entry from the database explicitly using session ID
    game_state_entry = db.query(GameStateDB).filter(GameStateDB.session_id == session_id_str).first()

    # Explicitly handle the scenario where no game state is found for the provided session ID
    if not game_state_entry:
        raise HTTPException(status_code=404, detail="Game state not found.")

    # Parse the stored JSON game state explicitly
    game_state = game_state_entry.game_state

    # Retrieve labyrinth ID explicitly from the game state
    labyrinth_id = game_state['game_info']['labyrinth_id']

    # Fetch all tiles explicitly associated with this labyrinth from the database
    tiles_from_db = db.query(Tile).filter(Tile.labyrinth_id == labyrinth_id).all()

    # Prepare container explicitly for visual tile representations for frontend visualization
    visual_tiles = []

    # Iterate explicitly over each tile fetched from the database
    for tile_db in tiles_from_db:
        # open_directions already deserialized to a list, sort explicitly for consistent filenames
        directions = sorted(tile_db.open_directions)

        # Generate explicit tile image filename based on tile type and open directions
        tile_image = get_image_filename(tile_db.type, directions)

        # Find corresponding tile from in-memory state to retrieve entities and map objects
        tile_state = next((t for t in game_state['labyrinth'].values()
                           if t['x'] == tile_db.x and t['y'] == tile_db.y), {})

        # Retrieve explicitly detailed entity data directly associated with this tile
        entities_on_tile = [
            {
                "id": entity['id'],      # Unique identifier of the entity
                "type": entity['type'],  # Explicit entity type (player, enemy, npc)
            }
            for entity in tile_state.get('entities', [])
        ]

        # Structure tile information explicitly for frontend visualization, taking all fields from DB
        visual_tile = {
            "x": tile_db.x,                              # Explicit X-coordinate on the labyrinth grid
            "y": tile_db.y,                              # Explicit Y-coordinate on the labyrinth grid
            "image": tile_image,                         # Explicit image filename representing the tile visually
            "revealed": tile_db.revealed,                # Explicitly from DB to ensure correctness
            "entities": entities_on_tile,                # Entities explicitly retrieved from game state
            "map_object": tile_state.get('map_object'),  # Explicit additional map object if applicable
            "tile_code": tile_db.tile_code,              # Thematic tile code explicitly from DB
            "thematic_area": tile_db.thematic_area       # Thematic area explicitly from DB
        }

        # Append explicitly prepared tile data to visual tiles container
        visual_tiles.append(visual_tile)

    # Explicitly return structured visual tiles data for frontend rendering
    return {"tiles": visual_tiles}
