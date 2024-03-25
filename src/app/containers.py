from __future__ import annotations

from src.app.ports.infrastructure.db.user_repositories import (
    DummyUserRepository,
)
from src.app.ports.services.user_service import UserServiceHttp


class ServiceContainer:
    user_service: UserServiceHttp = UserServiceHttp(DummyUserRepository())

    def __init__(self) -> None:
        pass

    def __call__(self) -> ServiceContainer:
        return self
