from pydantic import BaseModel

class ClientJoinRequest(BaseModel):
    client_id: str
