# routes/api.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from models.game_session import GameSession
from models.mobile_client import MobileClient
from uuid import UUID, uuid4
from datetime import datetime
from schemas import ClientJoinRequest, GameSessionCreateRequest, PlayerStatus, SessionStatus
from db.session import get_db
from utils.corrected_labyrinth_backend_seed_fixed import generate_labyrinth
from state import session_readiness, lock
from realtime import broadcast_session_update
from realtime import broadcast_game_started
from models import Entity, SessionPlayerCharacter
from realtime import broadcast_character_selected
from realtime import broadcast_character_released



router = APIRouter()

@router.post("/api/game_sessions/{session_id}/start_game")
async def start_game(session_id: str):
    await broadcast_game_started(session_id)
    return {"message": "Game started broadcast sent"}

@router.get('/api/game_sessions')
async def get_game_sessions(db: Session = Depends(get_db)):
    sessions = db.query(GameSession).all()
    return {"sessions": sessions}

@router.post('/api/game_sessions/{session_id}/join')
async def join_game_session(session_id: UUID, request: ClientJoinRequest, db: Session = Depends(get_db)):
    session = db.query(GameSession).filter(GameSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail='Session not found')

    existing_client = db.query(MobileClient).filter(MobileClient.client_id == request.client_id).first()
    if existing_client:
        return {'message': 'Client already connected'}

    new_client = MobileClient(
        client_id=request.client_id,
        game_session_id=session.id,
        connected_at=datetime.utcnow()
    )
    db.add(new_client)
    db.commit()
    db.refresh(new_client)

    # Explicitly register client in readiness tracking upon joining
    with lock:
        session_str_id = str(session_id)
        if session_str_id not in session_readiness:
            session_readiness[session_str_id] = {}

        session_readiness[session_str_id][request.client_id] = False

        players = [
            PlayerStatus(client_id=cid, ready=ready)
            for cid, ready in session_readiness[session_str_id].items()
        ]
        session_status = SessionStatus(players=players, all_ready=False)
        await broadcast_session_update(session_str_id, session_status.dict())

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


@router.get('/api/game_sessions/{session_id}/clients')
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

@router.post('/api/game_sessions/create')
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

@router.post('/api/game_sessions/leave')
async def leave_game_session(request: ClientJoinRequest, db: Session = Depends(get_db)):
    existing_client = db.query(MobileClient).filter(MobileClient.client_id == request.client_id).first()
    if not existing_client:
        raise HTTPException(status_code=404, detail='Client not connected to any session')

    session_id = str(existing_client.game_session_id)

    # Explicitly remove player from DB
    db.delete(existing_client)
    db.commit()

    # Explicitly remove player from session readiness tracking and broadcast state
    with lock:
        if session_id in session_readiness and request.client_id in session_readiness[session_id]:
            del session_readiness[session_id][request.client_id]

        players = [
            PlayerStatus(client_id=cid, ready=ready)
            for cid, ready in session_readiness.get(session_id, {}).items()
        ]
        all_ready = all(player.ready for player in players) if players else False

        session_status = SessionStatus(players=players, all_ready=all_ready)
        await broadcast_session_update(session_id, session_status.dict())

    return {'message': 'Disconnected successfully'}

@router.get("/api/game_sessions/client_state/{client_id}")
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

@router.post("/api/game_sessions/{session_id}/toggle_readiness", response_model=SessionStatus)
async def toggle_readiness(session_id: str, payload: PlayerStatus, db: Session = Depends(get_db)):
    with lock:
        if session_id not in session_readiness:
            session_readiness[session_id] = {}

        # Explicitly fetch selection to confirm a character is selected before marking ready
        selection = db.query(SessionPlayerCharacter).filter_by(
            session_id=session_id, client_id=payload.client_id
        ).first()

        if not selection and payload.ready:
            # Explicitly prevent players without a character selection from marking as ready
            raise HTTPException(status_code=400, detail="Select a character before marking ready.")

        if selection:
            # Explicitly lock/unlock character selection based on readiness
            selection.locked = payload.ready
            db.commit()

        session_readiness[session_id][payload.client_id] = payload.ready

        players = [
            PlayerStatus(client_id=cid, ready=ready)
            for cid, ready in session_readiness[session_id].items()
        ]

        all_ready = all(p.ready for p in players)
        session_status = SessionStatus(players=players, all_ready=all_ready)

        await broadcast_session_update(session_id, session_status.dict())

        return session_status




@router.get("/api/game_sessions/{session_id}/status", response_model=SessionStatus)
async def get_session_status(session_id: str):
    with lock:
        players = []
        if session_id in session_readiness:
            players = [
                PlayerStatus(client_id=cid, ready=ready)
                for cid, ready in session_readiness[session_id].items()
            ]
        all_ready = all(p.ready for p in players) if players else False
        return SessionStatus(players=players, all_ready=all_ready)

@router.delete('/api/game_sessions/destroy_all')
async def destroy_all_sessions(db: Session = Depends(get_db)):
    try:
        db.query(MobileClient).delete()  # Delete connected mobile clients first to avoid foreign key constraints
        db.query(GameSession).delete()
        db.commit()
        return {"message": "All sessions destroyed successfully"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.get('/api/game_sessions/user/{client_id}')
async def get_user_game_sessions(client_id: str, db: Session = Depends(get_db)):
    sessions = db.query(GameSession).filter(GameSession.creator_client_id == client_id).all()
    return {"sessions": sessions}

@router.get('/api/game_sessions/user/{client_id}/joined')
async def get_joined_game_sessions(client_id: str, db: Session = Depends(get_db)):
    sessions = db.query(GameSession).join(MobileClient).filter(
        MobileClient.client_id == client_id,
        GameSession.creator_client_id != client_id
    ).all()

    return {"sessions": sessions}

# Explicitly fetch characters that are not yet selected by any player (locked OR unlocked)
@router.get("/api/game_sessions/{session_id}/available_characters")
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
@router.post("/api/game_sessions/{session_id}/select_character")
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


@router.post("/api/game_sessions/{session_id}/release_character")
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
@router.get("/api/game_sessions/{session_id}/selected_characters")
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






