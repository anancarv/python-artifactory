"""
Definition of all autho models.
"""

from typing import Tuple, Optional

from pydantic import BaseModel, SecretStr


class AuthModel(BaseModel):
    """Models an auth response."""

    url: str
    auth: Tuple[str, SecretStr]
    verify: bool = True
    cert: Optional[str] = None


class ApiKeyModel(BaseModel):
    """Models an api key."""

    apiKey: SecretStr


class PasswordModel(BaseModel):
    """Models a password."""

    password: SecretStr


class AccessTokenModel(BaseModel):
    """Model an access token."""

    access_token: str
    expires_in: Optional[int] = 3600
    scope: str
    refresh_token: Optional[str] = None
    token_type: str
