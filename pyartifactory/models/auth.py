"""
Definition of all auth models.
"""
from __future__ import annotations

from pydantic import BaseModel, SecretStr


class AuthModel(BaseModel):
    """Models an auth response."""

    url: str
    auth: tuple[str, SecretStr]
    verify: bool = True
    cert: str | None | None = None
    api_version: int = 1


class ApiKeyModel(BaseModel):
    """Models an api key."""

    apiKey: SecretStr


class PasswordModel(BaseModel):
    """Models a password."""

    password: SecretStr


class AccessTokenModel(BaseModel):
    """Model an access token."""

    access_token: str
    expires_in: int | None = 3600
    scope: str
    refresh_token: str | None = None
    token_type: str
