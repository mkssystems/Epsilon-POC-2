# realtime.py

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

    # Immediately broadcast the current session state explicitly
    with lock:
        players = [
            PlayerStatus(client_id=cid, ready=ready)
            for cid, ready in session_readiness.get(session_id, {}).items()
        ]
        all_ready = all(player.ready for player in players) if players else False

        session_status = SessionStatus(players=players, all_ready=all_ready)
        await broadcast_session_update(session_id, session_status.dict())

async def disconnect_from_session(session_id: str, websocket: WebSocket):
    if session_id in active_connections:
        active_connections[session_id] = [
            conn for conn in active_connections[session_id]
            if conn["websocket"] != websocket
        ]

        if not active_connections[session_id]:
            del active_connections[session_id]

    # Do NOT remove player from session_readiness explicitly here!
    # Players remain registered explicitly until they explicitly leave via API

async def broadcast_session_update(session_id: str, message: dict):
    if session_id in active_connections:
        for connection in active_connections[session_id]:
            try:
                await connection["websocket"].send_json(message)
            except Exception:
                pass  # Ignore failed sends

async def broadcast_game_started(session_id: str):
    message = {"event": "game_started"}
    await broadcast_session_update(session_id, message)

async def broadcast_character_selected(session_id: str, client_id: str, entity_id: str):
    message = {
        "event": "character_selected",
        "client_id": client_id,
        "entity_id": entity_id
    }
    await broadcast_session_update(session_id, message)


async def broadcast_character_released(session_id: str, client_id: str, entity_id: str):
    message = {
        "event": "character_released",
        "client_id": client_id,
        "entity_id": entity_id
    }
    await broadcast_session_update(session_id, message)


# ping-pong
@router.websocket("/ws/{session_id}/{client_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str, client_id: str):
    await connect_to_session(session_id, client_id, websocket)
    try:
        while True:
            message = await websocket.receive_text()
            if message:
                data = json.loads(message)
                if data.get('type') == 'ping':
                    await websocket.send_text(json.dumps({"type": "pong"}))  # explicitly respond to ping
    except WebSocketDisconnect:
        await disconnect_from_session(session_id, websocket)



from fastapi import APIRouter
import json
from game_logic.game_flow_controller import GameFlowController

def mount_websocket_routes(app):
    router = APIRouter()

    @router.websocket("/ws/{session_id}/{client_id}")
    async def websocket_endpoint(websocket: WebSocket, session_id: str, client_id: str):
        await connect_to_session(session_id, client_id, websocket)
        try:
            while True:
                # Explicitly wait for incoming JSON messages from the frontend
                message_text = await websocket.receive_text()

                # Parse incoming message explicitly to JSON
                try:
                    data = json.loads(message_text)
                except json.JSONDecodeError:
                    await websocket.send_json({"type": "error", "message": "Invalid JSON format."})
                    continue

                # Explicit handling for specific WebSocket actions
                if data.get('action') == 'start_game':
                    # Handle 'start_game' action explicitly
                    print(f"[INFO] Received 'start_game' from client {client_id} for session {session_id}")

                    # Instantiate game logic controller explicitly and start the game
                    game_controller = GameFlowController(session_id)

                    try:
                        game_controller.start_game()

                        # Broadcast explicitly to all connected players
                        await broadcast_game_started(session_id)

                        # Send confirmation explicitly back to initiating client
                        await websocket.send_json({
                            "type": "game_started",
                            "session_id": session_id,
                            "message": "Game has started successfully."
                        })

                        print(f"[INFO] Game started successfully for session: {session_id}")

                    except Exception as e:
                        await websocket.send_json({
                            "type": "error",
                            "message": f"Error starting game: {str(e)}"
                        })

                        print(f"[ERROR] Error starting game for session {session_id}: {str(e)}")

                else:
                    # Handle other actions or send default response
                    await websocket.send_json({
                        "type": "error",
                        "message": "Unknown action provided."
                    })

        except WebSocketDisconnect:
            await disconnect_from_session(session_id, websocket)

    app.include_router(router)
