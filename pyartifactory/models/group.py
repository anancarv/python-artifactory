"""
Definition of all group models.
"""
from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel


class Group(BaseModel):
    """Models a group."""

    name: str
    description: Optional[str] = None
    autoJoin: bool = False
    adminPrivileges: bool = False
    realm: Optional[str] = None
    realmAttributes: Optional[str] = None
    watchManager: bool = False
    policyManager: bool = False
    userNames: Optional[List[str]] = None


class SimpleGroup(BaseModel):
    """Models a simple group."""

    name: str
    uri: str
