from pydantic import BaseModel
from typing import Optional

class ClientJoinRequest(BaseModel):
    client_id: str

class GameSessionCreateRequest(BaseModel):
    seed: Optional[str] = None
    labyrinth_id: Optional[str] = None
