from datetime import datetime, timedelta
from pydantic import BaseModel


class PayLoad(BaseModel):
    message: str
    expiration_date: datetime = datetime.now() + timedelta(minutes=2)

    @property
    def valid(self) -> bool:
        return datetime.now() < self.expiration_date
