from pydantic import BaseModel


class SecretsClientError(BaseModel):
    message: str
    code: int
