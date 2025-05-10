# routes/player_ready.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from models.game_session import GameSession
from models.mobile_client import MobileClient
from realtime import broadcast_session_update
from db.session import get_db
from game_logic.validation.sync_validator import validate_sync
from game_logic.data.game_state import GamePhaseName, PhaseInfo
from utils.db_utils import load_initial_game_state, save_game_state_to_db
from datetime import datetime

router = APIRouter()

@router.post("/api/game/{session_id}/player-ready")
async def player_ready(session_id: str, payload: dict, db: Session = Depends(get_db)):
    client_id = payload.get("client_id")
    client_turn = payload.get("turn_number")
    client_phase = payload.get("phase")

    # Validate payload inputs explicitly
    if not all([client_id, client_turn is not None, client_phase]):
        raise HTTPException(status_code=400, detail="client_id, turn_number, and phase are explicitly required.")

    # Explicit session validation
    session = db.query(GameSession).filter(GameSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Game session explicitly not found.")

    # Validate synchronization explicitly
    validation_result = validate_sync(session_id, client_turn, client_phase, db)

    if validation_result["status"] == "mismatch":
        raise HTTPException(status_code=409, detail={
            "detail": "State mismatch explicitly detected.",
            "backend_turn": validation_result["backend_turn"],
            "backend_phase": validation_result["backend_phase"],
            "client_turn": validation_result["client_turn"],
            "client_phase": validation_result["client_phase"]
        })
    elif validation_result["status"] == "error":
        raise HTTPException(status_code=500, detail=validation_result["detail"])

    # Correctly retrieve and update client readiness explicitly
    client = db.query(MobileClient).filter(
        MobileClient.client_id == client_id,
        MobileClient.game_session_id == session_id
    ).first()

    if not client:
        raise HTTPException(status_code=404, detail="Client explicitly not found for this session.")

    client.is_ready = True
    db.commit()

    # Check explicitly if all clients are ready
    all_clients = db.query(MobileClient).filter(MobileClient.game_session_id == session_id).all()
    if all(client.is_ready for client in all_clients):
        # Load current game state explicitly
        game_state = load_initial_game_state(db, session_id)

        # Check and explicitly update from TURN_0 to INITIAL_PLACEMENT if applicable
        if game_state.phase.name == GamePhaseName.TURN_0:
            game_state.phase = PhaseInfo(
                name=GamePhaseName.INITIAL_PLACEMENT,
                number=None,  # No sub-phase number explicitly required here
                is_end_turn=False,
                started_at=datetime.utcnow()
            )

            # Save explicitly updated state to the database
            save_game_state_to_db(db, game_state)

            # Explicitly broadcast updated game state
            await broadcast_session_update(session_id, {
                "event": "phase_transition",
                "new_phase": game_state.phase.name.value,
                "timestamp": game_state.phase.started_at.isoformat()
            })

        # Explicitly broadcast all players ready event
        await broadcast_session_update(session_id, {
            "event": "all_players_ready",
            "session_id": session_id
        })

    # Return confirmation explicitly
    return {"status": "ready confirmed"}
