# realtime.py

from fastapi import WebSocket, WebSocketDisconnect
from typing import Dict, List
import asyncio
import json
from state import session_readiness, lock
from schemas import PlayerStatus, SessionStatus
from config import WEBSOCKET_INACTIVITY_TIMEOUT  # Explicitly imported timeout
from game_logic.game_flow_controller import GameFlowController
from fastapi import APIRouter

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


def mount_websocket_routes(app):
    router = APIRouter()

    @router.websocket("/ws/{session_id}/{client_id}")
    async def websocket_endpoint(websocket: WebSocket, session_id: str, client_id: str):
        await connect_to_session(session_id, client_id, websocket)

        try:
            while True:
                try:
                    # Explicitly wait for incoming JSON messages with inactivity timeout
                    message_text = await asyncio.wait_for(
                        websocket.receive_text(), timeout=WEBSOCKET_INACTIVITY_TIMEOUT
                    )
                except asyncio.TimeoutError:
                    # Explicit timeout handling
                    print(f"[INFO] Connection to client {client_id} in session {session_id} explicitly closed due to inactivity ({WEBSOCKET_INACTIVITY_TIMEOUT} sec).")
                    await websocket.close()
                    await disconnect_from_session(session_id, websocket)
                    break

                # Parse incoming message explicitly to JSON
                try:
                    data = json.loads(message_text)
                except json.JSONDecodeError:
                    await websocket.send_json({"type": "error", "message": "Invalid JSON format."})
                    continue

                # Explicit handling for specific WebSocket actions
                if data.get('action') == 'start_game':
                    print(f"[INFO] Received 'start_game' from client {client_id} for session {session_id}")

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
                        await websocket.send_json({"type": "error", "message": f"Error starting game: {str(e)}"})
                        print(f"[ERROR] Error starting game for session {session_id}: {str(e)}")

                # Explicitly handle ping messages from frontend (heartbeat)
                elif data.get('type') == 'ping':
                    print(f"[INFO] Received 'ping' from client {client_id} (session: {session_id})")
                    await websocket.send_json({"type": "pong"})
                    print(f"[INFO] Sent 'pong' to client {client_id} (session: {session_id})")

                else:
                    # Handle unknown actions explicitly or send default response
                    await websocket.send_json({"type": "error", "message": "Unknown action provided."})

        except WebSocketDisconnect:
            # Explicitly log client-side triggered disconnections
            print(f"[INFO] WebSocketDisconnect explicitly triggered by client {client_id} (session: {session_id})")
            await disconnect_from_session(session_id, websocket)

        except Exception as e:
            # Explicitly log unexpected errors and perform safe disconnection
            print(f"[ERROR] Unexpected error explicitly occurred for client {client_id} (session: {session_id}): {str(e)}")
            await disconnect_from_session(session_id, websocket)

    app.include_router(router)
