from __future__ import annotations

from pyartifactory import ArtifactoryArtifact
from pyartifactory.models import AuthModel

URL = "http://localhost:8080/artifactory"
AUTH = ("user", "password_or_apiKey")
ARTIFACT_REPO = "my_repository"


# Test that timeout is used by requests
def test_get_artifact_folder_info_timeout(mocker):
    artifactory = ArtifactoryArtifact(AuthModel(url=URL, auth=AUTH, timeout=1))
    artifactory.session = mocker.MagicMock()
    mocker.patch("pyartifactory.models.artifact.ArtifactFolderInfoResponse.model_validate")
    artifactory.session.return_value = mocker.MagicMock()
    artifactory.info("ARTIFACT_REPO")
    artifactory.session.get.call_args_list[0][1]["timeout"] == 1
