"""
Import all models here.
"""
from __future__ import annotations

from typing import Union

from .artifact import (
    ArtifactFileInfoResponse,
    ArtifactFolderInfoResponse,
    ArtifactInfoResponse,
    ArtifactPropertiesResponse,
    ArtifactStatsResponse,
)
from .auth import AccessTokenModel, ApiKeyModel, AuthModel, PasswordModel
from .build import (
    BuildAgent,
    BuildArtifact,
    BuildCreateRequest,
    BuildDeleteRequest,
    BuildDiffResponse,
    BuildDiffResponseDetail,
    BuildError,
    BuildInfo,
    BuildInfoDetail,
    BuildListResponse,
    BuildModules,
    BuildPromotionRequest,
    BuildPromotionResult,
    BuildProperties,
    BuildRun,
    Run,
    SimpleBuild,
)
from .group import Group, SimpleGroup
from .permission import Permission, PermissionV2, SimplePermission
from .repository import (
    FederatedRepository,
    FederatedRepositoryResponse,
    LocalRepository,
    LocalRepositoryResponse,
    RemoteRepository,
    RemoteRepositoryResponse,
    SimpleRepository,
    VirtualRepository,
    VirtualRepositoryResponse,
)
from .user import BaseUserModel, NewUser, SimpleUser, User, UserResponse

AnyRepositoryResponse = Union[
    LocalRepositoryResponse,
    VirtualRepositoryResponse,
    RemoteRepositoryResponse,
    FederatedRepositoryResponse,
]

AnyRepository = Union[LocalRepository, VirtualRepository, RemoteRepository, FederatedRepository]
AnyPermission = Union[Permission, PermissionV2]

__all__ = [
    "ArtifactFileInfoResponse",
    "ArtifactFolderInfoResponse",
    "ArtifactInfoResponse",
    "ArtifactPropertiesResponse",
    "ArtifactStatsResponse",
    "AccessTokenModel",
    "ApiKeyModel",
    "AuthModel",
    "PasswordModel",
    "Group",
    "SimpleGroup",
    "Permission",
    "PermissionV2",
    "SimplePermission",
    "LocalRepository",
    "LocalRepositoryResponse",
    "RemoteRepository",
    "RemoteRepositoryResponse",
    "FederatedRepository",
    "FederatedRepositoryResponse",
    "SimpleRepository",
    "VirtualRepository",
    "VirtualRepositoryResponse",
    "User",
    "UserResponse",
    "BaseUserModel",
    "NewUser",
    "SimpleUser",
    "AnyRepositoryResponse",
    "AnyRepository",
    "AnyPermission",
    "SimpleBuild",
    "BuildListResponse",
    "Run",
    "BuildRun",
    "BuildArtifact",
    "BuildModules",
    "BuildAgent",
    "BuildInfoDetail",
    "BuildInfo",
    "BuildPromotionResult",
    "BuildPromotionRequest",
    "BuildProperties",
    "BuildError",
    "BuildDeleteRequest",
    "BuildDiffResponseDetail",
    "BuildDiffResponse",
    "BuildCreateRequest",
]
