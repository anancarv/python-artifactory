"""
Import all models here.
"""
from typing import Union

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

from .artifact import ArtifactPropertiesResponse, ArtifactStatsResponse
from .permission import Permission, SimplePermission


AnyRepositoryResponse = Union[
    LocalRepositoryResponse, VirtualRepositoryResponse, RemoteRepositoryResponse
]

AnyRepository = Union[LocalRepository, VirtualRepository, RemoteRepository]
