from typing import Dict
import threading

# Shared global state
session_readiness: Dict[str, Dict[str, bool]] = {}
lock = threading.Lock()
