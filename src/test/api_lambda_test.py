from datetime import datetime
from urllib.parse import urlparse

from aws_lambda_powertools.utilities.data_classes import APIGatewayProxyEventV2
from aws_lambda_powertools.utilities.typing import LambdaContext

from src.app.domain.cipher.models.messages import PayLoad
from src.lambda_functions.api_lambda import lambda_handler, service


class MockLambdaContext(LambdaContext):

    def __init__(self) -> None:
        self._function_name = "test"
        self._memory_limit_in_mb = 128
        self._invoked_function_arn = "testarn"
        self._aws_request_id = "12345"


def test_create_secret():
    lambda_context = MockLambdaContext()
    data = {
        "path": "/hush/secrets",
        "httpMethod": "POST",
        "body": "this is a secret",
        "requestContext": {"path": "/hush/secrets", "domainName": "localhost"},
    }
    event = APIGatewayProxyEventV2(data=data)
    response = lambda_handler(event, lambda_context)
    parsed = urlparse(response["body"])

    assert parsed.scheme == "https"
    assert data["path"] in parsed.path
    assert parsed.hostname == data["requestContext"]["domainName"]
    assert response["statusCode"] == 200
    assert response["body"] != ""


def test_decrypt_secret():
    lambda_context = MockLambdaContext()
    secret = "this is a secret"
    data = {
        "httpMethod": "POST",
        "path": "/hush/secrets",
        "body": secret,
        "requestContext": {"path": "/hush/secrets", "domainName": "localhost"},
    }
    event = APIGatewayProxyEventV2(data=data)
    response = lambda_handler(event, lambda_context)
    parsed = urlparse(response["body"])

    message = parsed.path.removeprefix("/hush/secrets/")
    cipher_data = {"httpMethod": "GET", "path": f"/hush/secrets/{message}"}
    cipher_event = APIGatewayProxyEventV2(data=cipher_data)
    cipher_response = lambda_handler(cipher_event, lambda_context)

    assert parsed.scheme == "https"
    assert data["requestContext"]["path"] in parsed.path
    assert parsed.hostname == data["requestContext"]["domainName"]
    assert cipher_response["statusCode"] == 200
    assert cipher_response["body"] == secret


def test_invalid_secret():
    lambda_context = MockLambdaContext()
    secret = "this is a secret"
    payload: PayLoad = PayLoad(message=secret, expiration_date=datetime.now())
    ciphertext = service.encrypt(payload)

    cipher_data = {"path": f"/hush/secrets/{ciphertext}", "httpMethod": "GET"}

    cipher_event = APIGatewayProxyEventV2(data=cipher_data)

    cipher_response = lambda_handler(cipher_event, lambda_context)

    assert cipher_response["statusCode"] == 404
    assert cipher_response["body"] == "Token expired"
