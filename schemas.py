from pydantic import BaseModel
from typing import Optional

class ClientJoinRequest(BaseModel):
    client_id: str

class GameSessionCreateRequest(BaseModel):
    size: int
    creator_client_id: str
    scenario_name: str
    difficulty: str
    max_players: int

from pydantic import BaseModel
from typing import List

class PlayerStatus(BaseModel):
    client_id: str
    ready: bool

class SessionStatus(BaseModel):
    players: List[PlayerStatus]
    all_ready: bool
