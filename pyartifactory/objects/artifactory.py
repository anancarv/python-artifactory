from __future__ import annotations

from typing import Optional, Tuple, Union

from pydantic import SecretStr

from pyartifactory.models.auth import AuthModel
from pyartifactory.objects.artifact import ArtifactoryArtifact
from pyartifactory.objects.group import ArtifactoryGroup
from pyartifactory.objects.permission import ArtifactoryPermission
from pyartifactory.objects.repository import ArtifactoryRepository
from pyartifactory.objects.security import ArtifactorySecurity
from pyartifactory.objects.user import ArtifactoryUser


class Artifactory:
    """Models artifactory."""

    def __init__(
        self,
        url: str,
        auth: Tuple[str, SecretStr],
        verify: Union[bool, str] = True,
        cert: Optional[str] = None,
        api_version: int = 1,
    ):
        self.artifactory = AuthModel(url=url, auth=auth, verify=verify, cert=cert, api_version=api_version)
        self.users = ArtifactoryUser(self.artifactory)
        self.groups = ArtifactoryGroup(self.artifactory)
        self.security = ArtifactorySecurity(self.artifactory)
        self.repositories = ArtifactoryRepository(self.artifactory)
        self.artifacts = ArtifactoryArtifact(self.artifactory)
        self.permissions = ArtifactoryPermission(self.artifactory)
