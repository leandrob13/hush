from src.app.domain.user.services.user_services import UserService

from loguru import logger

from src.app.ports.infrastructure.db.user_repositories import (
    DummyUserRepository,
)


class UserServiceHttp(UserService):

    def __init__(self, user_repository: DummyUserRepository) -> None:
        self.user_repository = user_repository
