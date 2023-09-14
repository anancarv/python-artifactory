"""
Definition of all group models.
"""
from __future__ import annotations

from pydantic import BaseModel


class Group(BaseModel):
    """Models a group."""

    name: str
    description: str | None = None
    autoJoin: bool = False
    adminPrivileges: bool = False
    realm: str | None = None
    realmAttributes: str | None = None
    watchManager: bool = False
    policyManager: bool = False
    userNames: list[str] | None = None


class SimpleGroup(BaseModel):
    """Models a simple group."""

    name: str
    uri: str
