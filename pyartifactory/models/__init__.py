"""
Import all models here.
"""
from typing import Union, Type

from .auth import AuthModel, ApiKeyModel, PasswordModel, AccessTokenModel
from .group import Group, SimpleGroup
from .user import NewUser, UserResponse, BaseUserModel, SimpleUser, User
from .repository import (
    LocalRepository,
    LocalRepositoryResponse,
    VirtualRepository,
    VirtualRepositoryResponse,
    RemoteRepository,
    RemoteRepositoryResponse,
    SimpleRepository,
)

from .artifact import (
    ArtifactPropertiesResponse,
    ArtifactStatsResponse,
    ArtifactFileInfoResponse,
    ArtifactFolderInfoResponse,
    ArtifactInfoResponse,
)
from .permission import Permission, PermissionV2, SimplePermission


AnyRepositoryResponse = Union[
    LocalRepositoryResponse, VirtualRepositoryResponse, RemoteRepositoryResponse
]

AnyRepository = Union[LocalRepository, VirtualRepository, RemoteRepository]
AnyPermission = Union[Permission, PermissionV2]
