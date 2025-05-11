# realtime.py

from fastapi import WebSocket, WebSocketDisconnect, APIRouter, Depends
from typing import Dict, List
import asyncio
import json
from schemas import PlayerStatus, SessionStatus
from config import WEBSOCKET_INACTIVITY_TIMEOUT, WEBSOCKET_PING_ONLY_TIMEOUT
import time
from datetime import datetime
from enum import Enum
from db.session import get_db

active_connections: Dict[str, List[Dict]] = {}

from sqlalchemy.orm import Session
from models.mobile_client import MobileClient
from schemas import PlayerStatus, SessionStatus
from db.session import get_db  # Explicit DB session handler

async def connect_to_session(session_id: str, client_id: str, websocket: WebSocket, db: Session):
    # Accept WebSocket connection explicitly
    await websocket.accept()

    # Register the WebSocket connection explicitly
    if session_id not in active_connections:
        active_connections[session_id] = []
    active_connections[session_id].append({"client_id": client_id, "websocket": websocket})

    # Explicitly fetch readiness status directly from DB
    all_clients = db.query(MobileClient).filter(
        MobileClient.game_session_id == session_id
    ).all()

    # Construct players readiness from DB entries explicitly
    players = [
        PlayerStatus(client_id=client.client_id, ready=client.is_ready)
        for client in all_clients
    ]

    # Explicitly calculate overall readiness state
    all_ready = all(client.is_ready for client in all_clients)

    session_status = SessionStatus(players=players, all_ready=all_ready)

    # Explicitly broadcast readiness state retrieved from DB
    await broadcast_session_update(session_id, session_status.dict())


async def disconnect_from_session(session_id: str, websocket: WebSocket):
    if session_id in active_connections:
        active_connections[session_id] = [
            conn for conn in active_connections[session_id]
            if conn["websocket"] != websocket
        ]
        if not active_connections[session_id]:
            del active_connections[session_id]

# Serializer to handle special data types (datetime, enum)
def custom_serializer(o):
    if isinstance(o, datetime):
        return o.isoformat()
    if isinstance(o, Enum):
        return o.value
    raise TypeError(f"Type {type(o)} not serializable")

async def broadcast_session_update(session_id: str, message: dict):
    if not isinstance(message, dict):
        print(f"[ERROR] Invalid message: {message}")
        return

    serialized_message = json.loads(json.dumps(message, default=custom_serializer))

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
    async def websocket_endpoint(websocket: WebSocket, session_id: str, client_id: str, db: Session = Depends(get_db)):
        await connect_to_session(session_id, client_id, websocket, db)
        last_non_ping_time = time.time()

        try:
            while True:
                try:
                    message_text = await asyncio.wait_for(
                        websocket.receive_text(), timeout=WEBSOCKET_INACTIVITY_TIMEOUT
                    )
                    print(f"[DEBUG] Raw WebSocket message from client {client_id}: {message_text}")
                except asyncio.TimeoutError:
                    print(f"[INFO] Connection to client {client_id} in session {session_id} closed due to inactivity.")
                    await websocket.close()
                    await disconnect_from_session(session_id, websocket)
                    break

                try:
                    data_dict = json.loads(message_text)
                    if not isinstance(data_dict, dict):
                        raise ValueError(f"Parsed JSON is not an object: type={type(data_dict)}")
                except (json.JSONDecodeError, ValueError) as e:
                    print(f"[ERROR] JSON parse error from client {client_id}: {e}, original message: {message_text}")
                    await websocket.send_json({"type": "error", "message": "Invalid JSON format."})
                    continue

                message_type = data_dict.get('type')

                if message_type == 'ping':
                    await websocket.send_json({"type": "pong"})
                    print(f"[INFO] Received 'ping' from client {client_id} (session: {session_id})")
                    if (time.time() - last_non_ping_time) > WEBSOCKET_PING_ONLY_TIMEOUT:
                        print(f"[INFO] Connection closed (ping-only) for client {client_id}, session {session_id}.")
                        await websocket.close()
                        await disconnect_from_session(session_id, websocket)
                        break

                elif message_type == 'intro_completed':
                    # DB-driven readiness update explicitly
                    client_entry = db.query(MobileClient).filter(
                        MobileClient.client_id == client_id,
                        MobileClient.game_session_id == session_id
                    ).first()

                    if client_entry:
                        client_entry.is_ready = True
                        db.commit()

                        all_clients = db.query(MobileClient).filter(
                            MobileClient.game_session_id == session_id
                        ).all()

                        players = [
                            PlayerStatus(client_id=client.client_id, ready=client.is_ready)
                            for client in all_clients
                        ]

                        all_ready = all(client.is_ready for client in all_clients)

                        session_status = SessionStatus(players=players, all_ready=all_ready)

                        await broadcast_session_update(session_id, session_status.dict())

                        if all_ready:
                            await broadcast_session_update(session_id, {
                                "event": "all_players_ready",
                                "message": "All players have completed the intro."
                            })

                        print(f"[INFO] Player {client_id} marked as ready in session {session_id}.")
                    else:
                        await websocket.send_json({"type": "error", "message": "Client not found in session."})
                        print(f"[WARN] Client {client_id} not found in session {session_id} during intro_completed.")

                else:
                    last_non_ping_time = time.time()
                    await websocket.send_json({"type": "error", "message": f"Unknown action '{message_type}' provided."})
                    print(f"[WARN] Unknown action received from client {client_id}: {data_dict}")

        except WebSocketDisconnect:
            print(f"[INFO] WebSocketDisconnect by client {client_id} (session: {session_id})")
            await disconnect_from_session(session_id, websocket)
        except Exception as e:
            print(f"[ERROR] Unexpected error for client {client_id} (session: {session_id}): {e}")
            await disconnect_from_session(session_id, websocket)

    app.include_router(router)

