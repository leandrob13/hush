import logging
from typing import Annotated

from src.app.adapters.http.errors.user_errors import UserNotFoundDTO
from src.app.containers import ServiceContainer
from fastapi import APIRouter, Depends, HTTPException

from src.app.adapters.http.dtos.user_dtos import ViabilityResponseDTO
from src.app.domain.user.models.errors import ViabilityError
from src.app.domain.user.models.evaluations import Viability
from src.app.domain.user.models.users import IdentityType

router = APIRouter()

logger = logging.getLogger("Router")

ServiceDependency = Annotated[ServiceContainer, Depends()]


@router.on_event("shutdown")
async def shutdown() -> None:
    logger.info("Closing services client sessions.")
    pass


@router.get("/validate/{id_type}/{id}/", response_model=ViabilityResponseDTO)
async def validate(
    id_type: IdentityType,
    id: int,
    container: ServiceDependency,
) -> ViabilityResponseDTO:
    credit_client_response = await container.user_service.process_client(id, id_type)
    match credit_client_response:
        case Viability() as viability:
            message = f"Cliente ha sido {'Pre Aprobado' if credit_client_response.approved else 'Rechazado'}"
            logger.info(message)
            return ViabilityResponseDTO.from_viability_response(viability)
        case ViabilityError() as error:
            raise HTTPException(
                status_code=404, detail=UserNotFoundDTO(message=error.detail).dict()
            )
