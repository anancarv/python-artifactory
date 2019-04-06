from typing import Tuple

from pydantic import BaseModel, SecretStr


class AuthModel(BaseModel):
    url: str
    api_key: SecretStr = None
    auth: Tuple[str, SecretStr] = None


class ApiKeyModel(BaseModel):
    apiKey: SecretStr = None


class PasswordModel(BaseModel):
    password: SecretStr = None
