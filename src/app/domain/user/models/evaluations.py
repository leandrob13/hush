from pydantic import BaseModel


class Viability(BaseModel):
    approved: bool
    reason: str
    score: int
