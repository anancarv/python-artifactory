"""
Import all models here.
"""
from typing import Union

from .group import Group, SimpleGroup
from .permission import Permission, SimplePermission
from .auth import AuthModel, ApiKeyModel, PasswordModel, AccessTokenModel
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
from .aql import Aql
from .artifact import (
    ArtifactPropertiesResponse,
    ArtifactStatsResponse,
    ArtifactFileInfoResponse,
    ArtifactFolderInfoResponse,
    ArtifactInfoResponse,
)


AnyRepositoryResponse = Union[
    LocalRepositoryResponse, VirtualRepositoryResponse, RemoteRepositoryResponse
]

AnyRepository = Union[LocalRepository, VirtualRepository, RemoteRepository]
