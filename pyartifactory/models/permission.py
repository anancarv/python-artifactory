"""
Definition of all permission models.
"""

from enum import Enum
from typing import List, Dict, Optional

from pydantic import BaseModel


class SimplePermission(BaseModel):
    """Models a simple permission."""

    name: str
    uri: str


class PermissionEnum(str, Enum):
    """Enumerates a permission."""

    admin = "m"
    delete = "d"
    deploy = "w"
    annotate = "n"
    read = "r"


class PrincipalsPermission(BaseModel):
    """Models a principals permission."""

    users: Optional[Dict[str, List[PermissionEnum]]] = None
    groups: Optional[Dict[str, List[PermissionEnum]]] = None


class Permission(BaseModel):
    """Models a permission."""

    name: str
    includesPattern: str = "**"
    excludesPattern: str = ""
    repositories: List[str]
    principals: PrincipalsPermission
