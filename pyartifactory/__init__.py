from typing import Tuple

from pyartifactory.models.Artifactory import ArtifactoryModel
from pyartifactory.objects import ArtfictoryUser

__version__ = "0.1.0"


class Artifactory:
    def __init__(
        self, url: str = None, api_key: str = None, auth: Tuple[str, str] = None
    ):
        self.artifactory = ArtifactoryModel(url=url, api_key=api_key, auth=auth)

        self.users = ArtfictoryUser(self.artifactory)
