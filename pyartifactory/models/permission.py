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


class PermissionEnumV2(str, Enum):
    """Enumerates a permission."""

    manage = "manage"
    delete = "delete"
    write = "write"
    annotate = "annotate"
    read = "read"


class PrincipalsPermissionV2(BaseModel):
    """Models a principals permission API v2."""

    users: Optional[Dict[str, List[PermissionEnumV2]]] = None
    groups: Optional[Dict[str, List[PermissionEnumV2]]] = None


class RepoV2(BaseModel):
    """Models a repo v2 API."""

    repositories: List[str]
    actions: PrincipalsPermissionV2
    # Note: the Jfrog API changed these parameters names in v2,
    # from 'includesPattern' to 'include-patterns'. Because they are not
    # valid Python identifiers we chose a camelCase name for the variable,
    # and specify the alias Pydantic should look for when deserializing.
    # Note that when serializing this model Pydantic will by default use the
    # identifier name, *not* the alias, so you need to pass the parameter
    # by_alias=True when exporting (like permission.json(by_alias=True))
    includePatterns: List[str] = Field(["**"], alias="include-patterns")
    excludePatterns: List[str] = Field([""], alias="exclude-patterns")

    class Config:
        # We need this to be able to use 'includePatterns' in the constructor
        allow_population_by_field_name = True


class PermissionV2(BaseModel):
    """Models a permission v2 API."""

    name: str
    repo: RepoV2
