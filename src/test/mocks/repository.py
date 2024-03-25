from typing import Any, Text, Dict

from src.app.db import BaseRepository
import uuid

from src.app.adapters.http.dtos import PersonResponse


class RepositoryMock(BaseRepository):
    database: Dict[Text, Any] = {}

    async def insert_person(self, person_response: PersonResponse) -> Text:
        self.database.update({str(uuid.uuid4()): person_response.dict()})
        return "uuid"
