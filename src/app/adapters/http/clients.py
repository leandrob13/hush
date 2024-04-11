import sys
from httpx import Client, Response

from src.app.adapters.http.dtos import SecretResponse
from loguru import logger

from src.app.adapters.http.errors import SecretsClientError

logger.add(sys.stdout, colorize=True, serialize=True)


class SecretsHttpClient:
    session_token: str
    port: str

    def __init__(self, session_token: str, port: str) -> None:
        self.session_token = session_token
        self.port = port

    def secret_by_name(self, secret_name: str) -> SecretResponse | SecretsClientError:
        url = f"http://localhost:{self.port}/secretsmanager/get"
        params = {"secretId": secret_name}
        headers = {"X-Aws-Parameters-Secrets-Token": self.session_token}

        with Client(params=params, headers=headers) as http_client:
            response = http_client.get(url)

        match response:
            case Response(status_code=200) as res:
                json_response = res.json()
                logger.info(f"Layer response: {json_response.get('Name', 'None')}")
                # return SecretResponse(SecretString=json_response.get("SecretString"))  # .validate(res.json())
                return SecretResponse.validate(json_response)
            case Response(status_code=400) as res:
                logger.error(
                    "Error requesting secrets", response=res.text, request=res.request
                )
                return SecretsClientError(
                    message="Error fetching the secret", code=response.status_code
                )
            case _:
                return SecretsClientError(
                    message=f"Unhandled error for code {response.status_code}",
                    code=response.status_code,
                )

    """
    def secret_by_name(self, secret_name: str) -> SecretResponse | SecretsClientError:
        client = boto3.client('secretsmanager')
        try:
            response = client.get_secret_value(SecretId=secret_name)
            secret = response.get("SecretString")
            return SecretResponse(SecretString=secret)

        except Exception as err:
            logger.exception("Error requesting secrets", error=err)
            return SecretsClientError(
                message="Error fetching the secret", code=400
            )"""
