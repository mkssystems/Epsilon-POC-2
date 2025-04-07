from pydantic import BaseModel
from typing import Optional

class ClientJoinRequest(BaseModel):
    client_id: str

class GameSessionCreateRequest(BaseModel):
    size: int                  # Explicitly required
    
