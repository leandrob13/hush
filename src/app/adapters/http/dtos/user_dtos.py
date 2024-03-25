from typing import Text

from pydantic import BaseModel

from src.app.domain.user.models.evaluations import Viability


class ViabilityResponseDTO(BaseModel):
    approved: bool
    reason: Text

    @staticmethod
    def from_viability_response(response: Viability) -> "ViabilityResponseDTO":
        return ViabilityResponseDTO(approved=response.approved, reason=response.reason)
