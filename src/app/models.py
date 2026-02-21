
from pydantic import BaseModel, Field

class Packet(BaseModel):
    id: str = Field(..., description="Identifiant du paquet")
    payload: str | bytes | dict = Field(..., description="Contenu")
    timestamp: float | None = Field(default=None, description="Epoch secondes")
