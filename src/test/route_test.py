import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from httpx import Response

from src.http.routes import router
from src.app.containers import ServiceContainer
from src.app.adapters.http.dtos.user_dtos import ViabilityResponseDTO


base_url = "http://testserver"


@pytest.fixture
def tapp() -> FastAPI:
    fa_app = FastAPI()
    fa_app.include_router(router)
    fa_app.dependency_overrides[ServiceContainer] = ServiceContainer
    return fa_app


# @pytest.mark.asyncio
def test_get_person(tapp: FastAPI) -> None:
    client = TestClient(tapp)
    response: Response = client.get(f"/validate/CC/1")
    viability_response = ViabilityResponseDTO.parse_obj(response.json())
    assert response.status_code == 200
    assert viability_response.approved
    assert viability_response.reason == "Is a natural person"
