import json
from datetime import datetime
import os
from enum import Enum  # Explicit import for serializer consistency

# Custom serializer explicitly handling datetime and Enum serialization
def json_serializer(obj):
    if isinstance(obj, datetime):
        return obj.isoformat()
    if isinstance(obj, Enum):
        return obj.value
    raise TypeError(f"Type {type(obj)} not serializable")

def log_game_state(session_id: str, game_state: dict):
    """
    Explicitly appends a serialized game state to a log file for debugging purposes.

    Args:
        session_id (str): Unique identifier for the game session.
        game_state (dict): Serialized game state dictionary explicitly provided.
    """
    # Explicitly set directory path for Render persistent disk
    logs_dir = "/var/data/game_state_logs"

    # Ensure the logs directory explicitly exists, create if necessary
    os.makedirs(logs_dir, exist_ok=True)
    
    # Explicitly define log file path per session ID
    log_file_path = os.path.join(logs_dir, f"{session_id}_game_state.log")

    # Prepare log entry with an explicit timestamp for clarity
    log_entry = {
        "logged_at": datetime.utcnow(),
        "game_state": game_state
    }

    # Append explicitly serialized JSON log entry to the log file with custom serializer
    with open(log_file_path, "a") as log_file:
        log_file.write(json.dumps(log_entry, default=json_serializer) + "\n")
