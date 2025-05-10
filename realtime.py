# realtime.py

from fastapi import WebSocket, WebSocketDisconnect
from typing import Dict, List
import asyncio
import json
from state import session_readiness, lock
from schemas import PlayerStatus, SessionStatus
from config import WEBSOCKET_INACTIVITY_TIMEOUT, WEBSOCKET_PING_ONLY_TIMEOUT
from fastapi import APIRouter
import time
from datetime import datetime

active_connections: Dict[str, List[Dict]] = {}

async def connect_to_session(session_id: str, client_id: str, websocket: WebSocket):
    await websocket.accept()
    if session_id not in active_connections:
        active_connections[session_id] = []
    active_connections[session_id].append({"client_id": client_id, "websocket": websocket})

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

async def broadcast_session_update(session_id: str, message: dict):
    if not isinstance(message, dict):
        print(f"[ERROR] Invalid message: {message}")
        return

    # Explicitly convert datetime to string
    def datetime_converter(o):
        if isinstance(o, datetime):
            return o.isoformat()
        raise TypeError(f"Type {type(o)} not serializable")

    serialized_message = json.loads(json.dumps(message, default=datetime_converter))

    if session_id in active_connections:
        for connection in active_connections[session_id]:
            try:
                await connection["websocket"].send_json(serialized_message)
            except Exception as e:
                print(f"[ERROR] WebSocket send_json exception: {e}")

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
        last_non_ping_time = time.time()

        try:
            while True:
                try:
                    message_text = await asyncio.wait_for(
                        websocket.receive_text(), timeout=WEBSOCKET_INACTIVITY_TIMEOUT
                    )
                except asyncio.TimeoutError:
                    print(f"[INFO] Connection to client {client_id} in session {session_id} explicitly closed due to inactivity.")
                    await websocket.close()
                    await disconnect_from_session(session_id, websocket)
                    break

                # Explicitly parse incoming WebSocket message as JSON
                try:
                    data_dict = json.loads(message_text)
                    if not isinstance(data_dict, dict):
                        raise ValueError("Parsed JSON is not an object.")
                except (json.JSONDecodeError, ValueError) as e:
                    print(f"[ERROR] JSON parse error explicitly: {e}")
                    await websocket.send_json({"type": "error", "message": "Invalid JSON format."})
                    continue

                if data_dict.get('type') == 'ping':
                    print(f"[INFO] Received 'ping' from client {client_id} (session: {session_id})")
                    await websocket.send_json({"type": "pong"})
                    if (time.time() - last_non_ping_time) > WEBSOCKET_PING_ONLY_TIMEOUT:
                        print(f"[INFO] Connection explicitly closed (ping-only) for client {client_id}, session {session_id}.")
                        await websocket.close()
                        await disconnect_from_session(session_id, websocket)
                        break

                elif data_dict.get('type') == 'intro_completed':
                    with lock:
                        if session_id not in session_readiness:
                            session_readiness[session_id] = {}
                        session_readiness[session_id][client_id] = True

                        # Explicitly update players' readiness status
                        players = [
                            PlayerStatus(client_id=cid, ready=ready)
                            for cid, ready in session_readiness[session_id].items()
                        ]
                        all_ready = all(player.ready for player in players)

                        # Explicitly broadcast updated session status
                        session_status = SessionStatus(players=players, all_ready=all_ready)
                        await broadcast_session_update(session_id, session_status.dict())

                        # Explicitly notify if all players are ready
                        if all_ready:
                            await broadcast_session_update(session_id, {
                                "event": "all_players_ready",
                                "message": "All players have completed the intro."
                            })

                    print(f"[INFO] Player {client_id} explicitly marked as ready in session {session_id}.")

                else:
                    last_non_ping_time = time.time()
                    await websocket.send_json({"type": "error", "message": "Unknown action provided."})

        except WebSocketDisconnect:
            print(f"[INFO] WebSocketDisconnect explicitly triggered by client {client_id} (session: {session_id})")
            await disconnect_from_session(session_id, websocket)

        except Exception as e:
            print(f"[ERROR] Unexpected error explicitly occurred for client {client_id} (session: {session_id}): {str(e)}")
            await disconnect_from_session(session_id, websocket)

    app.include_router(router)
