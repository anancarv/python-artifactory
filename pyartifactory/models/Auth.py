from typing import Tuple

from pydantic import BaseModel, SecretStr


class AuthModel(BaseModel):
    url: str
    auth: Tuple[str, SecretStr] = None
    verify: bool = True
    cert: str = None


class ApiKeyModel(BaseModel):
    apiKey: SecretStr = None


class PasswordModel(BaseModel):
    password: SecretStr = None
