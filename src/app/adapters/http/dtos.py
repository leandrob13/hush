from pydantic import BaseModel, Field


class SecretResponse(BaseModel):
    secret_string: str = Field(alias="SecretString")
