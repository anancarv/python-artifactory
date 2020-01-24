"""
Definition of all group models.
"""
from typing import Optional
from pydantic import BaseModel


class Group(BaseModel):
    """Models a group."""

    name: str
    description: Optional[str] = None
    autoJoin: bool = False
    adminPrivileges: bool = False
    realm: Optional[str] = None
    realmAttributes: Optional[str] = None


class SimpleGroup(BaseModel):
    """Models a simple group."""

    name: str
    uri: str
