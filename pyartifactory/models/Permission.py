from enum import Enum
from typing import List, Dict, Optional, Set

from pydantic import BaseModel


class SimplePermission(BaseModel):
    name: str
    uri: str


class PermissionEnum(str, Enum):
    admin = "m"
    delete = "d"
    deploy = "w"
    annotate = "n"
    read = "r"


class PrincipalsPermission(BaseModel):
    users: Optional[Dict[str, Set[PermissionEnum]]] = None
    groups: Optional[Dict[str, Set[PermissionEnum]]] = None


class Permission(BaseModel):
    name: str
    includesPattern: str = "**"
    excludesPattern: str = ""
    repositories: Set[str]
    principals: PrincipalsPermission
