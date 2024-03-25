from pydantic import BaseModel
from enum import Enum


class IdentityType(Enum):
    CC = "CC"
    CE = "CE"
    PASSPORT = "PASSPORT"
    NIT = "NIT"


class PersonType(Enum):
    NAT = "NAT"
    JUR = "JUR"


class User(BaseModel):
    name: str
    identity_number: int
    identity_type: IdentityType
    person_type: PersonType


class CreditClient(User):
    pass
