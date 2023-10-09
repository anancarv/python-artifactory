"""
Import all object definitions here.
"""
from __future__ import annotations

import contextlib
from importlib.metadata import PackageNotFoundError, version

from pyartifactory.models.auth import AccessTokenModel
from pyartifactory.objects.artifact import ArtifactoryArtifact
from pyartifactory.objects.artifactory import Artifactory
from pyartifactory.objects.group import ArtifactoryGroup
from pyartifactory.objects.permission import ArtifactoryPermission
from pyartifactory.objects.repository import ArtifactoryRepository
from pyartifactory.objects.security import ArtifactorySecurity
from pyartifactory.objects.user import ArtifactoryUser

__all__ = [
    "AccessTokenModel",
    "Artifactory",
    "ArtifactoryGroup",
    "ArtifactoryArtifact",
    "ArtifactoryPermission",
    "ArtifactoryRepository",
    "ArtifactorySecurity",
    "ArtifactoryUser",
]

with contextlib.suppress(PackageNotFoundError):
    __version__ = version("pyartifactory")
