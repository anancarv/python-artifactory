"""
Definition of all auth models.
"""
from __future__ import annotations

from typing import Optional, Tuple, Union

from pydantic import BaseModel, SecretStr


class AuthModel(BaseModel):
    """Models an auth response."""

    url: str
    auth: Tuple[str, SecretStr]
    verify: Union[bool, str] = True
    cert: Optional[str] = None
    api_version: int = 1
    timeout: Optional[int] = None


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
