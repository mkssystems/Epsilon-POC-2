# realtime.py (explicitly balanced DB & WebSocket stability)

from fastapi import WebSocket, WebSocketDisconnect, APIRouter
from typing import Dict, List
import asyncio
import json
import threading
from schemas import PlayerStatus, SessionStatus
from config import WEBSOCKET_INACTIVITY_TIMEOUT, WEBSOCKET_PING_ONLY_TIMEOUT
import time
from datetime import datetime
from enum import Enum

from db.session import SessionLocal  # Explicit DB session
from models.mobile_client import MobileClient

active_connections: Dict[str, List[Dict]] = {}
session_readiness: Dict[str, Dict[str, bool]] = {}  # Explicit in-memory cache
lock = threading.Lock()  # Explicit thread-safe operations

# Custom serializer to handle special data types (datetime, enum)
def custom_serializer(o):
    if isinstance(o, datetime):
        return o.isoformat()
    if isinstance(o, Enum):
        return o.value
    raise TypeError(f"Type {type(o)} not serializable")

async def broadcast_session_update(session_id: str, message: dict):
    serialized_message = json.loads(json.dumps(message, default=custom_serializer))
    if session_id in active_connections:
        for connection in active_connections[session_id]:
            try:
                await connection["websocket"].send_json(serialized_message)
            except Exception as e:
                print(f"[ERROR] WebSocket send_json exception: {e}")

async def connect_to_session(session_id: str, client_id: str, websocket: WebSocket):
    await websocket.accept()
    if session_id not in active_connections:
        active_connections[session_id] = []
    active_connections[session_id].append({"client_id": client_id, "websocket": websocket})

    # Explicitly initialize DB session once per connection
    db = SessionLocal()
    try:
        # Fetch readiness explicitly from DB at connection start
        clients = db.query(MobileClient).filter(MobileClient.game_session_id == session_id).all()

        with lock:
            session_readiness[session_id] = {client.client_id: client.is_ready for client in clients}

        players = [PlayerStatus(client_id=c.client_id, ready=c.is_ready) for c in clients]
        all_ready = all(c.is_ready for c in clients)

        session_status = SessionStatus(players=players, all_ready=all_ready)
        await broadcast_session_update(session_id, session_status.dict())
    finally:
        db.close()

async def disconnect_from_session(session_id: str, websocket: WebSocket):
    if session_id in active_connections:
        active_connections[session_id] = [
            conn for conn in active_connections[session_id]
            if conn["websocket"] != websocket
        ]
        if not active_connections[session_id]:
            del active_connections[session_id]

async def broadcast_game_started(session_id: str):
    await broadcast_session_update(session_id, {"event": "game_started"})

async def broadcast_character_selected(session_id: str, client_id: str, entity_id: str):
    await broadcast_session_update(session_id, {
        "event": "character_selected",
        "client_id": client_id,
        "entity_id": entity_id
    })

async def broadcast_character_released(session_id: str, client_id: str, entity_id: str):
    await broadcast_session_update(session_id, {
        "event": "character_released",
        "client_id": client_id,
        "entity_id": entity_id
    })

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
                    print(f"[DEBUG] WebSocket message from {client_id}: {message_text}")
                except asyncio.TimeoutError:
                    print(f"[INFO] Client {client_id} disconnected due to inactivity.")
                    await websocket.close()
                    await disconnect_from_session(session_id, websocket)
                    break

                try:
                    data_dict = json.loads(message_text)
                    if not isinstance(data_dict, dict):
                        raise ValueError("Parsed JSON is not an object.")
                except (json.JSONDecodeError, ValueError):
                    await websocket.send_json({"type": "error", "message": "Invalid JSON format."})
                    continue

                message_type = data_dict.get('type')

                if message_type == 'ping':
                    await websocket.send_json({"type": "pong"})
                    if (time.time() - last_non_ping_time) > WEBSOCKET_PING_ONLY_TIMEOUT:
                        print(f"[INFO] Client {client_id} ping-only timeout.")
                        await websocket.close()
                        await disconnect_from_session(session_id, websocket)
                        break

                elif message_type == 'intro_completed':
                    db = SessionLocal()
                    try:
                        client_entry = db.query(MobileClient).filter(
                            MobileClient.client_id == client_id,
                            MobileClient.game_session_id == session_id
                        ).first()
                        if client_entry:
                            client_entry.is_ready = True
                            db.commit()

                            # Update readiness explicitly in memory
                            with lock:
                                session_readiness[session_id][client_id] = True

                            players = [
                                PlayerStatus(client_id=cid, ready=ready)
                                for cid, ready in session_readiness[session_id].items()
                            ]
                            all_ready = all(player.ready for player in players)

                            await broadcast_session_update(session_id, SessionStatus(players=players, all_ready=all_ready).dict())

                            if all_ready:
                                await broadcast_session_update(session_id, {
                                    "event": "all_players_ready",
                                    "message": "All players have completed the intro."
                                })
                        else:
                            await websocket.send_json({"type": "error", "message": "Client not found."})
                    finally:
                        db.close()

                elif message_type == 'request_readiness':
                    node = data_dict.get('node')  # explicitly read node
                    with lock:
                        players = [
                            PlayerStatus(client_id=cid, ready=ready)
                            for cid, ready in session_readiness.get(session_id, {}).items()
                        ]
                        all_ready = all(player.ready for player in players)
                
                    await websocket.send_json({
                        "type": "readiness_status",
                        "node": node,  # Explicitly add node here
                        "players": [p.dict() for p in players],
                        "all_ready": all_ready
                    })

                else:
                    await websocket.send_json({"type": "error", "message": f"Unknown action '{message_type}'."})

        except WebSocketDisconnect:
            await disconnect_from_session(session_id, websocket)
        except Exception as e:
            print(f"[ERROR] WebSocket error: {e}")
            await disconnect_from_session(session_id, websocket)

    app.include_router(router)
