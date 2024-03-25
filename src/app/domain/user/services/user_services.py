from typing import Optional

from src.app.domain.user.models.errors import ViabilityError
from src.app.domain.user.models.evaluations import Viability
from src.app.domain.user.models.users import PersonType, IdentityType, User
from src.app.domain.user.repositories.user_repositories import UserRepository


class UserService:
    user_repository: UserRepository

    async def get_credit_client(
        self, identity_number: int, identity_type: IdentityType
    ) -> Optional[User]:
        return await self.user_repository.get_user(identity_number, identity_type)

    async def evaluate_credit_client(self, user: User) -> Viability:
        approved = user.person_type == PersonType.NAT
        return Viability(
            approved=approved,
            reason="Is a natural person" if approved else "Not a natural person",
            score=0,
        )

    async def process_client(
        self, identity_number: int, identity_type: IdentityType
    ) -> Viability | ViabilityError:
        client = await self.get_credit_client(identity_number, identity_type)
        return (
            await self.evaluate_credit_client(client)
            if client is not None
            else ViabilityError(detail="Client not found")
        )
