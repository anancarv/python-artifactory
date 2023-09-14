"""
Definition of all user related models.
"""
from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, EmailStr, HttpUrl, SecretStr


class SimpleUser(BaseModel):
    """Models a simple user."""

    name: str
    uri: HttpUrl
    realm: str | None = None


class BaseUserModel(BaseModel):
    """
    Models a base user.
    https://www.jfrog.com/confluence/display/JFROG/Security+Configuration+JSON#SecurityConfigurationJSON-application/vnd.org.jfrog.artifactory.security.User+json
    """

    name: str
    admin: bool | None = False
    profileUpdatable: bool | None = True
    disableUIAccess: bool | None = False
    internalPasswordDisabled: bool | None = False
    groups: list[str] | None = None


class NewUser(BaseUserModel):
    """Models a new user."""

    email: EmailStr
    password: SecretStr


class User(BaseUserModel):
    """Models a user."""

    email: EmailStr | None = None


class UserResponse(BaseUserModel):
    """Models a user response."""

    email: EmailStr
    lastLoggedIn: datetime | None = None
    realm: str | None = None
    offlineMode: bool = False
