from pydantic import BaseModel
from typing import List, Optional


class Group(BaseModel):
    name: str
    description: str = None
    autoJoin: bool = False
    adminPrivileges: bool = False
    realm: Optional[str] = None
    realmAttributes: Optional[str] = None


class SimpleGroup(BaseModel):
    name: str
    uri: str


class GroupList(BaseModel):
    groups: List[SimpleGroup] = None
