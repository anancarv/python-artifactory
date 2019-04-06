from typing import Tuple

from pyartifactory.models.Auth import AuthModel
from pyartifactory.objects import ArtfictoryUser, ArtfictoryGroup, ArtfictorySecurity

__version__ = "0.1.0"


class Artifactory:
    def __init__(self, url: str, api_key: str = None, auth: Tuple[str, str] = None):
        self.artifactory = AuthModel(url=url, api_key=api_key, auth=auth)
        self.users = ArtfictoryUser(self.artifactory)
        self.groups = ArtfictoryGroup(self.artifactory)
        self.security = ArtfictorySecurity(self.artifactory)
