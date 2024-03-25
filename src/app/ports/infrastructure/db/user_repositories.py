from typing import Optional

from src.app.domain.user.models.users import IdentityType, CreditClient, PersonType
from src.app.domain.user.repositories.user_repositories import UserRepository


class DummyUserRepository(UserRepository):

    async def get_user(
        self, identity_number: int, identity_type: IdentityType
    ) -> Optional[CreditClient]:
        person_type = PersonType.NAT if identity_number == 1 else PersonType.JUR
        return (
            CreditClient(
                name="Pedro",
                identity_number=identity_number,
                identity_type=identity_type,
                person_type=person_type,
            )
            if identity_number != 0
            else None
        )
