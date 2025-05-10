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
    # Define directory explicitly for game state logs
    logs_dir = "game_state_logs"

    # Ensure the logs directory explicitly exists, create if necessary
    os.makedirs(logs_dir, exist_ok=True)
    
    # Explicitly define log file path per session ID
    log_file_path = os.path.join(logs_dir, f"{session_id}_game_state.log")

    # Prepare log entry with an explicit timestamp for clarity
    log_entry = {
        "logged_at": datetime.utcnow().isoformat(),
        "game_state": game_state
    }

    # Append explicitly serialized JSON log entry to the log file
    with open(log_file_path, "a") as log_file:
        log_file.write(json.dumps(log_entry) + "\n")
