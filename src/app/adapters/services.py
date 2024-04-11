from src.app.adapters.http.clients import SecretsHttpClient
from src.app.adapters.http.dtos import SecretResponse
from src.app.adapters.http.errors import SecretsClientError
from src.app.domain.cipher.models.errors import CipherError
from src.app.domain.cipher.services.cipher_services import CipherService


class HttpService(CipherService):
    secrets_client: SecretsHttpClient
    salt_name: str
    passphrase_name: str

    def __init__(
        self, secrets_client: SecretsHttpClient, salt_name: str, passphrase_name: str
    ) -> None:
        self.secrets_client = secrets_client
        self.salt_name = salt_name
        self.passphrase_name = passphrase_name

    @property
    def salt(self) -> str | CipherError:
        return self.secret_by_name(self.salt_name)

    @property
    def passphrase(self) -> str | CipherError:
        return self.secret_by_name(self.passphrase_name)

    def secret_by_name(self, secret_name: str) -> str | CipherError:
        secret = self.secrets_client.secret_by_name(secret_name)
        match secret:
            case SecretResponse() as secretresponse:
                return secretresponse.secret_string
            case SecretsClientError(message=str(message)):
                return CipherError(message=message)
