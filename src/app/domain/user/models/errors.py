from pydantic import BaseModel


class ViabilityError(BaseModel):
    detail: str
