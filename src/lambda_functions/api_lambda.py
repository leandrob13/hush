from typing import Any
import os

from aws_lambda_powertools.event_handler import (
    APIGatewayRestResolver,
    CORSConfig,
    content_types,
)
from aws_lambda_powertools.logging import correlation_paths
from aws_lambda_powertools.logging.logger import Logger

from aws_lambda_powertools.utilities.data_classes import event_source
from aws_lambda_powertools.utilities.data_classes.api_gateway_proxy_event import (
    APIGatewayProxyEventV2,
)
from aws_lambda_powertools.utilities.typing import LambdaContext
from aws_lambda_powertools.event_handler.api_gateway import Response

from src.app.adapters.http.clients import SecretsHttpClient
from src.app.adapters.services import HttpService
from src.app.domain.cipher.models.errors import CipherError
from src.app.domain.cipher.models.messages import PayLoad

cors_config = CORSConfig()

app = APIGatewayRestResolver(cors=cors_config)

lambda_logger = Logger()

PASSPHRASE_NAME: str = os.getenv("PASSPHRASE_NAME", "NOP")

SALT_NAME = os.getenv("SALT_NAME", "NOP")

AWS_SESSION_TOKEN = os.environ.get("AWS_SESSION_TOKEN", "NOP")

service = HttpService(
    secrets_client=SecretsHttpClient(session_token=AWS_SESSION_TOKEN, port="2773"),
    salt_name=SALT_NAME,
    passphrase_name=PASSPHRASE_NAME,
)


@app.post("/hush/secrets")
def create_secret() -> Response[str]:
    body = app.current_event.decoded_body

    match body:
        case str(message):
            payload: PayLoad = PayLoad(message=message)
            ciphertext: str | CipherError = service.encrypt(payload)

            match ciphertext:
                case str(ct):
                    context = app.current_event.request_context
                    host = context.domain_name
                    path = context.path

                    return Response(
                        status_code=200,
                        body=f"https://{host}{path}/{ct}",
                        content_type=content_types.TEXT_PLAIN,
                    )
                case CipherError(message=m):
                    return Response(
                        status_code=400,
                        body=m,
                        content_type=content_types.TEXT_PLAIN,
                    )
        case None:
            return Response(
                status_code=400,
                body="Empty Message",
                content_type=content_types.TEXT_PLAIN,
            )


@app.get("/hush/secrets/<cipher>")
def get_secret(cipher: str) -> Response[str]:
    response = service.decrypt(cipher)

    match response:
        case PayLoad() as payload if payload.valid:
            return Response(
                status_code=200,
                body=payload.message,
                content_type=content_types.TEXT_PLAIN,
            )
        case PayLoad():
            return Response(
                status_code=404,
                body="Token expired",
                content_type=content_types.TEXT_PLAIN,
            )
        case CipherError() as ciphererror:
            return Response(
                status_code=400,
                body=ciphererror.message,
                content_type=content_types.TEXT_PLAIN,
            )


@lambda_logger.inject_lambda_context(
    correlation_id_path=correlation_paths.API_GATEWAY_REST
)
@event_source(data_class=APIGatewayProxyEventV2)
def lambda_handler(
    event: APIGatewayProxyEventV2, context: LambdaContext
) -> dict[str, Any]:
    lambda_logger.info("LAMBDA STARTED")
    return app.resolve(event, context)
