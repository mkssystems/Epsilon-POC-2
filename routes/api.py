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

router = APIRouter()

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

        # Immediately broadcast updated readiness state
        players = [
            PlayerStatus(client_id=cid, ready=ready)
            for cid, ready in session_readiness[session_str_id].items()
        ]
        session_status = SessionStatus(players=players, all_ready=False)
        broadcast_session_update(session_str_id, session_status.dict())

    return {
        'message': 'Connected successfully',
        'session_id': str(session.id),
        'map_seed': session.seed,
        'labyrinth_id': str(session.labyrinth_id),
        'start_x': session.start_x,
        'start_y': session.start_y,
        'size': session.size
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
        start_x=labyrinth.start_x,
        start_y=labyrinth.start_y,
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
        'start_x': new_session.start_x,
        'start_y': new_session.start_y
    }

@router.post('/api/game_sessions/leave')
async def leave_game_session(request: ClientJoinRequest, db: Session = Depends(get_db)):
    existing_client = db.query(MobileClient).filter(MobileClient.client_id == request.client_id).first()
    if not existing_client:
        raise HTTPException(status_code=404, detail='Client not connected to any session')

    db.delete(existing_client)
    db.commit()

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
                    "start_x": session.start_x,
                    "start_y": session.start_y
                }
            }
    return {"client_id": client_id, "connected_session": None, "session_details": None}

@router.post("/api/game_sessions/{session_id}/toggle_readiness", response_model=SessionStatus)
async def toggle_readiness(session_id: str, payload: PlayerStatus):
    with lock:
        if session_id not in session_readiness:
            session_readiness[session_id] = {}
        current_status = session_readiness[session_id].get(payload.client_id, False)
        session_readiness[session_id][payload.client_id] = not current_status

        players = [
            PlayerStatus(client_id=cid, ready=ready)
            for cid, ready in session_readiness[session_id].items()
        ]
        all_ready = all(p.ready for p in players)
        session_status = SessionStatus(players=players, all_ready=all_ready)

        broadcast_session_update(session_id, session_status.dict())

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
