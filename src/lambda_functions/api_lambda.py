import asyncio
from typing import Any

from aws_lambda_powertools import Tracer
from aws_lambda_powertools.event_handler import (
    APIGatewayRestResolver,
)
from aws_lambda_powertools.logging import correlation_paths
from aws_lambda_powertools.logging.logger import Logger
from aws_lambda_powertools.metrics.metrics import Metrics

from aws_lambda_powertools.utilities.data_classes import event_source
from aws_lambda_powertools.utilities.data_classes.api_gateway_proxy_event import (
    APIGatewayEventAuthorizer,
)
from aws_lambda_powertools.utilities.typing import LambdaContext
from aws_lambda_powertools.event_handler.exceptions import NotFoundError

from src.app.adapters.http.dtos.user_dtos import ViabilityResponseDTO
from src.app.domain.user.models.errors import ViabilityError
from src.app.domain.user.models.evaluations import Viability
from src.app.domain.user.models.users import IdentityType

from src.app.ports.infrastructure.db.user_repositories import (
    DummyUserRepository,
)
from src.app.ports.services.user_service import UserServiceHttp

app = APIGatewayRestResolver(enable_validation=True)

lambda_logger = Logger()
metrics = Metrics(namespace="pre-approved-app")
tracer = Tracer()

service = UserServiceHttp(DummyUserRepository())


@app.get("/ref-arch/validate/<id_type>/<id>")
@tracer.capture_method
def validate(
    id_type: str,
    id: int,
) -> ViabilityResponseDTO:
    credit_client_response = asyncio.run(
        service.process_client(id, IdentityType(id_type))
    )
    match credit_client_response:
        case Viability() as viability:
            message = f"Cliente ha sido {'Pre Aprobado' if viability.approved else 'Rechazado'}"
            lambda_logger.info(message)
            return ViabilityResponseDTO.from_viability_response(viability)
        case ViabilityError() as viabilityerror:
            lambda_logger.error(f"Cliente no encontrado", error=viabilityerror.dict())
            raise NotFoundError(viabilityerror.detail)


@lambda_logger.inject_lambda_context(
    correlation_id_path=correlation_paths.API_GATEWAY_REST
)
@metrics.log_metrics
@tracer.capture_lambda_handler(capture_response=False)
@event_source(data_class=APIGatewayEventAuthorizer)
def lambda_handler(
    event: APIGatewayEventAuthorizer, context: LambdaContext
) -> dict[str, Any]:
    lambda_logger.info("LAMBDA STARTED")
    return app.resolve(event.raw_event, context)
