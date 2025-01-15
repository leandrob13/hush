import base64
import json
from abc import ABC, abstractmethod

from loguru import logger
from cryptography.fernet import Fernet
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

from src.app.domain.cipher.models.errors import CipherError
from src.app.domain.cipher.models.messages import PayLoad


class CipherService(ABC):
    @property
    @abstractmethod
    def salt(self) -> str | CipherError:
        pass

    @property
    @abstractmethod
    def passphrase(self) -> str | CipherError:
        pass

    def generate_fernet(self) -> Fernet | CipherError:
        params = (self.salt, self.passphrase)
        logger.info("Successfully fetched secrets")
        match params:
            case (str(salt), str(passphrase)):
                logger.info("Starging Fernet generation")
                try:
                    kdf = PBKDF2HMAC(
                        algorithm=hashes.SHA256(),
                        length=32,
                        salt=str.encode(salt),
                        iterations=10000,
                        backend=default_backend(),
                    )
                    key = base64.urlsafe_b64encode(kdf.derive(passphrase.encode()))
                    logger.info("Generating Fernet")
                    return Fernet(key)
                except Exception as err:
                    logger.exception("Unknown error", err)
                    return CipherError(message=str(err))

            case (CipherError(message=m1), CipherError(message=m2)):
                message = f"No secrets retrieved: {m1} / {m2}"
                logger.error(f"Generating Fernet: {message}")
                return CipherError(message=message)
            case (CipherError(message=m1), str()) | (_, CipherError(message=m1)):
                message = f"No secrets retrieved: {m1}"
                logger.error(f"Generating Fernet: {message}")
                return CipherError(message=f"No secrets retrieved: {m1}")
            case (CipherError(message=m1), str()) | (_, CipherError(message=m1)):
                message = f"No secrets retrieved: {m1}"
                logger.error(f"Generating Fernet: {message}")
                return CipherError(message=f"No secrets retrieved: {m1}")
            case _:
                message = "No secrets retrieved"
                logger.error(f"Generating Fernet: {message}")
                return CipherError(message="No secrets retrieved")  # for completeness

    def encrypt(self, payload: PayLoad) -> str | CipherError:
        fernet = self.generate_fernet()
        match fernet:
            case Fernet() as f:
                return f.encrypt(payload.json().encode("utf-8")).decode("utf-8")
            case CipherError() as ciphererror:
                return ciphererror

    def decrypt(self, cipher: str) -> PayLoad | CipherError:
        fernet = self.generate_fernet()
        match fernet:
            case Fernet() as f:
                decrypted_message = f.decrypt(cipher.encode("utf-8"))
                return PayLoad.validate(json.loads(decrypted_message.decode("utf-8")))
            case CipherError() as ciphererror:
                return ciphererror
