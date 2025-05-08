# routes/player_ready.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from models.game_session import GameSession
from models.mobile_client import MobileClient
from realtime import broadcast_session_update
from db.session import get_db
from game_logic.validation.sync_validator import validate_sync  # Explicitly imported validation logic

router = APIRouter()

@router.post("/api/game/{session_id}/player-ready")
async def player_ready(session_id: str, payload: dict, db: Session = Depends(get_db)):
    client_id = payload.get("client_id")
    client_turn = payload.get("turn_number")
    client_phase = payload.get("phase")

    # Explicitly validate input presence
    if not all([client_id, client_turn is not None, client_phase]):
        raise HTTPException(status_code=400, detail="client_id, turn_number, and phase are explicitly required.")

    # Explicit session validation
    session = db.query(GameSession).filter(GameSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Game session explicitly not found.")

    # Explicit synchronization validation logic
    validation_result = validate_sync(session_id, client_turn, client_phase, db)

    if validation_result["status"] == "mismatch":
        # Explicit mismatch response
        raise HTTPException(status_code=409, detail={
            "detail": "State mismatch explicitly detected.",
            "backend_turn": validation_result["backend_turn"],
            "backend_phase": validation_result["backend_phase"],
            "client_turn": validation_result["client_turn"],
            "client_phase": validation_result["client_phase"]
        })
    elif validation_result["status"] == "error":
        raise HTTPException(status_code=500, detail=validation_result["detail"])

    # Explicitly handle readiness confirmation
    client = db.query(MobileClient).filter(
        MobileClient.id == client_id, 
        MobileClient.session_id == session_id
    ).first()

    if not client:
        raise HTTPException(status_code=404, detail="Client explicitly not found for this session.")

    client.is_ready = True  # Explicitly mark client as ready
    db.commit()

    # Explicitly check if all players are ready
    all_clients = db.query(MobileClient).filter(MobileClient.session_id == session_id).all()
    if all(client.is_ready for client in all_clients):
        # Explicitly broadcast that all players are ready
        await broadcast_session_update(session_id, {
            "event": "all_players_ready",
            "session_id": session_id
        })

    return {"status": "ready confirmed"}
