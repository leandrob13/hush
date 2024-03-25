from pydantic import BaseModel


class UserNotFoundDTO(BaseModel):
    message: str
