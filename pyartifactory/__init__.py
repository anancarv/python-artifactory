from typing import Tuple

from pyartifactory.models import AuthModel
from pyartifactory.objects import (
    ArtifactoryUser,
    ArtifactoryGroup,
    ArtifactorySecurity,
    ArtifactoryRepository,
    ArtifactoryPermission,
)

__version__ = "0.1.0"


class Artifactory:
    def __init__(
        self,
        url: str,
        auth: Tuple[str, str] = None,
        verify: bool = True,
        cert: str = None,
    ):
        self.artifactory = AuthModel(url=url, auth=auth, verify=verify, cert=cert)
        self.users = ArtifactoryUser(self.artifactory)
        self.groups = ArtifactoryGroup(self.artifactory)
        self.security = ArtifactorySecurity(self.artifactory)
        self.repositories = ArtifactoryRepository(self.artifactory)
        self.permissions = ArtifactoryPermission(self.artifactory)
