import json
from datetime import datetime
import os

def log_game_state(session_id: str, game_state: dict):
    """
    Explicitly appends a serialized game state to a log file for debugging purposes.

    Args:
        session_id (str): Unique identifier for the game session.
        game_state (dict): Serialized game state dictionary explicitly provided.
    """
    # Explicitly define the absolute path for persistent logging on Render
    logs_dir = "/var/data/game_state_logs"

    # Explicitly ensure the logs directory exists on the persistent disk, creating if necessary
    os.makedirs(logs_dir, exist_ok=True)

    # Explicitly construct the log file path using the session ID
    log_file_path = os.path.join(logs_dir, f"{session_id}_game_state.log")

    # Explicitly prepare the log entry including a timestamp for clarity and debugging
    log_entry = {
        "logged_at": datetime.utcnow().isoformat(),
        "game_state": game_state
    }

    # Explicitly append the serialized log entry as JSON to the log file
    with open(log_file_path, "a") as log_file:
        log_file.write(json.dumps(log_entry) + "\n")
