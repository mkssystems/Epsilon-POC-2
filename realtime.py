from fastapi import WebSocket, WebSocketDisconnect
from typing import Dict, List
import asyncio

# Each session_id maps to a list of WebSocket connections
active_connections: Dict[str, List[WebSocket]] = {}

async def connect_to_session(session_id: str, websocket: WebSocket):
    await websocket.accept()
    if session_id not in active_connections:
        active_connections[session_id] = []
    active_connections[session_id].append(websocket)

async def disconnect_from_session(session_id: str, websocket: WebSocket):
    if session_id in active_connections:
        active_connections[session_id].remove(websocket)
        if not active_connections[session_id]:
            del active_connections[session_id]

async def broadcast_session_update(session_id: str, message: dict):
    if session_id in active_connections:
        for connection in active_connections[session_id]:
            try:
                await connection.send_json(message)
            except Exception:
                pass  # Ignore failed sends

# WebSocket endpoint to include in main FastAPI app
def mount_websocket_routes(app):
    from fastapi import APIRouter

    router = APIRouter()

    @router.websocket("/ws/{session_id}")
    async def websocket_endpoint(websocket: WebSocket, session_id: str):
        await connect_to_session(session_id, websocket)
        try:
            while True:
                await websocket.receive_text()  # Just keep alive
        except WebSocketDisconnect:
            await disconnect_from_session(session_id, websocket)

    app.include_router(router)

