from pydantic import BaseModel
from typing import Optional

class ClientJoinRequest(BaseModel):
    client_id: str

class GameSessionCreateRequest(BaseModel):
    size: int                  # Explicitly required
    seed: Optional[str] = None  # Optional seed parameter added

from pydantic import BaseModel
from typing import List

class PlayerStatus(BaseModel):
    client_id: str
    ready: bool

class SessionStatus(BaseModel):
    players: List[PlayerStatus]
    all_ready: bool
