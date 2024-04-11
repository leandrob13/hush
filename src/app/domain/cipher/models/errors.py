from pydantic import BaseModel


class CipherError(BaseModel):
    message: str
