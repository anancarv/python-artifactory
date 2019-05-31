from typing import Tuple

from pyartifactory.models import AuthModel
from pyartifactory.objects import (
    ArtfictoryUser,
    ArtfictoryGroup,
    ArtfictorySecurity,
    ArtfictoryRepository,
    ArtifactoryArtifact,
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
        self.users = ArtfictoryUser(self.artifactory)
        self.groups = ArtfictoryGroup(self.artifactory)
        self.security = ArtfictorySecurity(self.artifactory)
        self.repositories = ArtfictoryRepository(self.artifactory)
        self.artifact = ArtifactoryArtifact(self.artifactory)
