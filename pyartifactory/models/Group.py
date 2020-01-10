from pydantic import BaseModel
from typing import Optional


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
