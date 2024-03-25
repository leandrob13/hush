from abc import ABC, abstractmethod
from typing import Optional

from src.app.domain.user.models.users import IdentityType, User


class UserRepository(ABC):

    @abstractmethod
    async def get_user(
        self, identity_number: int, identity_type: IdentityType
    ) -> Optional[User]:
        pass
