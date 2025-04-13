
from fastapi import WebSocket, WebSocketDisconnect
from typing import Dict, List
import asyncio
from state import session_readiness, lock
from schemas import PlayerStatus, SessionStatus

# Each session_id maps to a list of tuples (client_id, websocket)
active_connections: Dict[str, List[Dict]] = {}

async def connect_to_session(session_id: str, client_id: str, websocket: WebSocket):
    await websocket.accept()
    if session_id not in active_connections:
        active_connections[session_id] = []
    active_connections[session_id].append({"client_id": client_id, "websocket": websocket})

async def disconnect_from_session(session_id: str, websocket: WebSocket):
    disconnected_client_id = None
    if session_id in active_connections:
        for conn in active_connections[session_id]:
            if conn["websocket"] == websocket:
                disconnected_client_id = conn["client_id"]
                active_connections[session_id].remove(conn)
                break

        if not active_connections[session_id]:
            del active_connections[session_id]

    # Update readiness status and broadcast changes upon disconnect
    if disconnected_client_id:
        with lock:
            if session_id in session_readiness and disconnected_client_id in session_readiness[session_id]:
                del session_readiness[session_id][disconnected_client_id]

            players = [
                PlayerStatus(client_id=cid, ready=ready)
                for cid, ready in session_readiness.get(session_id, {}).items()
            ]

            all_ready = all(player.ready for player in players) if players else False

            session_status = SessionStatus(players=players, all_ready=all_ready)
            await broadcast_session_update(session_id, session_status.dict())

async def broadcast_session_update(session_id: str, message: dict):
    if session_id in active_connections:
        for connection in active_connections[session_id]:
            try:
                await connection["websocket"].send_json(message)
            except Exception:
                pass  # Ignore failed sends

# WebSocket endpoint to include in main FastAPI app
def mount_websocket_routes(app):
    from fastapi import APIRouter

    router = APIRouter()

    @router.websocket("/ws/{session_id}/{client_id}")
    async def websocket_endpoint(websocket: WebSocket, session_id: str, client_id: str):
        await connect_to_session(session_id, client_id, websocket)
        try:
            while True:
                await websocket.receive_text()  # Keep alive
        except WebSocketDisconnect:
            await disconnect_from_session(session_id, websocket)

    app.include_router(router)
