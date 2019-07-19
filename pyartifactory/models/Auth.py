from typing import Tuple, Optional

from pydantic import BaseModel, SecretStr


class AuthModel(BaseModel):
    url: str
    auth: Tuple[str, SecretStr]
    verify: bool = True
    cert: Optional[str] = None


class ApiKeyModel(BaseModel):
    apiKey: SecretStr


class PasswordModel(BaseModel):
    password: SecretStr
