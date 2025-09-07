"""
Definition of all permission models.
"""
from __future__ import annotations

from enum import Enum
from typing import Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field


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
    distribute = "x"
    managedXrayMeta = "mxm"


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
    distribute = "distribute"
    managedXrayMeta = "managedXrayMeta"


class PrincipalsPermissionV2(BaseModel):
    """Models a principals permission API v2."""

    users: Optional[Dict[str, List[PermissionEnumV2]]] = None
    groups: Optional[Dict[str, List[PermissionEnumV2]]] = None


class BasePermissionV2(BaseModel):
    """Models the base of a permission v2 API."""

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
    model_config = ConfigDict(populate_by_name=True)


class RepoV2(BasePermissionV2):
    """Models a repo v2 API."""


class BuildV2(BasePermissionV2):
    """Models a build v2 API."""

    includePatterns: List[str] = Field([""], alias="include-patterns")
    repositories: List[str] = ["artifactory-build-info"]


class ReleaseBundleV2(BasePermissionV2):
    """Models a releaseBundle v2 API."""

    excludePatterns: List[str] = Field([], alias="exclude-patterns")


class PermissionV2(BaseModel):
    """Models a permission v2 API."""

    name: str
    repo: Optional[RepoV2] = None
    build: Optional[BuildV2] = None
    releaseBundle: Optional[ReleaseBundleV2] = None
