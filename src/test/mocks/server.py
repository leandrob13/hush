from typing import Text

from fastapi import FastAPI

from src.app.adapters.http.dtos import PersonResponse

test_app = FastAPI()


@test_app.get("/person")
def persons(name: Text) -> PersonResponse:
    return PersonResponse(name=name)
