import pytest
import responses

from pyartifactory import ArtifactoryArtifact
from pyartifactory.exception import PropertyNotFoundException
from pyartifactory.models import (
    ArtifactPropertiesResponse,
    ArtifactStatsResponse,
    AuthModel,
)

URL = "http://localhost:8080/artifactory"
AUTH = ("user", "password_or_apiKey")
ARTIFACT_PATH = "my-repository/file.txt"
ARTIFACT_NEW_PATH = "my-second-repository/file.txt"
ARTIFACT_SHORT_PATH = "/file.txt"
LOCAL_FILE_LOCATION = "tests/test_artifacts.py"
ARTIFACT_ONE_PROPERTY = ArtifactPropertiesResponse(
    uri=f"{URL}/api/storage/{ARTIFACT_PATH}", properties={"prop1": ["value"]}
)
ARTIFACT_MULTIPLE_PROPERTIES = ArtifactPropertiesResponse(
    uri=f"{URL}/api/storage/{ARTIFACT_PATH}",
    properties={"prop1": ["value"], "prop2": ["another value", "with multiple parts"]},
)

ARTIFACT_STATS = ArtifactStatsResponse(
    uri="my_uri",
    downloadCount=0,
    lastDownloaded=0,
    remoteDownloadCount=0,
    remoteLastDownloaded=0,
)


@responses.activate
def test_deploy_artifact_success(mocker):
    responses.add(responses.PUT, f"{URL}/{ARTIFACT_PATH}", status=200)

    responses.add(
        responses.GET,
        f"{URL}/api/storage/{ARTIFACT_PATH}?properties[=x[,y]]",
        json=ARTIFACT_PROPERTIES.dict(),
        status=200,
    )
    artifactory = ArtifactoryArtifact(AuthModel(url=URL, auth=AUTH))
    mocker.spy(artifactory, "properties")
    artifact = artifactory.deploy(LOCAL_FILE_LOCATION, ARTIFACT_PATH)

    artifactory.properties.assert_called_once_with(ARTIFACT_PATH)
    assert artifact.dict() == ARTIFACT_PROPERTIES.dict()


@responses.activate
def test_download_artifact_success(tmp_path):
    artifact_name = ARTIFACT_PATH.split("/")[1]
    responses.add(
        responses.GET, f"{URL}/{ARTIFACT_PATH}", json=artifact_name, status=200
    )

    artifactory = ArtifactoryArtifact(AuthModel(url=URL, auth=AUTH))
    artifact = artifactory.download(ARTIFACT_PATH, str(tmp_path.resolve()))

    assert artifact == f"{tmp_path.resolve()}/{artifact_name}"
    assert (tmp_path / artifact_name).is_file()


@responses.activate
def test_get_artifact_single_property_success():
    responses.add(
        responses.GET,
        f"{URL}/api/storage/{ARTIFACT_PATH}?properties=prop1",
        json=ARTIFACT_ONE_PROPERTY.dict(),
        status=200,
    )

    artifactory = ArtifactoryArtifact(AuthModel(url=URL, auth=AUTH))
    artifact_properties = artifactory.properties(ARTIFACT_PATH, ["prop1"])
    assert artifact_properties.dict() == ARTIFACT_ONE_PROPERTY.dict()


@responses.activate
def test_get_artifact_multiple_properties_success():
    responses.add(
        responses.GET,
        f"{URL}/api/storage/{ARTIFACT_PATH}?properties=prop1,prop2",
        json=ARTIFACT_MULTIPLE_PROPERTIES.dict(),
        status=200,
    )

    artifactory = ArtifactoryArtifact(AuthModel(url=URL, auth=AUTH))
    artifact_properties = artifactory.properties(ARTIFACT_PATH, ["prop1", "prop2"])
    assert artifact_properties.dict() == ARTIFACT_MULTIPLE_PROPERTIES.dict()


@responses.activate
def test_get_artifact_multiple_properties_with_non_existing_properties_success():
    responses.add(
        responses.GET,
        f"{URL}/api/storage/{ARTIFACT_PATH}?properties=prop1,prop2,non_existing_prop",
        json=ARTIFACT_MULTIPLE_PROPERTIES.dict(),
        status=200,
    )

    artifactory = ArtifactoryArtifact(AuthModel(url=URL, auth=AUTH))
    artifact_properties = artifactory.properties(
        ARTIFACT_PATH, ["prop1", "prop2", "non_existing_prop"]
    )
    assert artifact_properties.dict() == ARTIFACT_MULTIPLE_PROPERTIES.dict()


@responses.activate
def test_get_artifact_all_properties_success():
    responses.add(
        responses.GET,
        f"{URL}/api/storage/{ARTIFACT_PATH}?properties",
        json=ARTIFACT_MULTIPLE_PROPERTIES.dict(),
        status=200,
    )

    artifactory = ArtifactoryArtifact(AuthModel(url=URL, auth=AUTH))
    artifact_properties = artifactory.properties(ARTIFACT_PATH)
    assert artifact_properties.dict() == ARTIFACT_MULTIPLE_PROPERTIES.dict()


@responses.activate
def test_get_artifact_property_not_found_error():
    responses.add(
        responses.GET,
        f"{URL}/api/storage/{ARTIFACT_PATH}?properties=a_property_not_found",
        json={"errors": [{"status": 404, "message": "No properties could be found."}]},
        status=404,
    )

    artifactory = ArtifactoryArtifact(AuthModel(url=URL, auth=AUTH))
    with pytest.raises(PropertyNotFoundException):
        artifactory.properties(ARTIFACT_PATH, properties=["a_property_not_found"])


@responses.activate
def test_get_artifact_stats_success():
    responses.add(
        responses.GET,
        f"{URL}/api/storage/{ARTIFACT_PATH}?stats",
        json=ARTIFACT_STATS.dict(),
        status=200,
    )

    artifactory = ArtifactoryArtifact(AuthModel(url=URL, auth=AUTH))
    artifact_stats = artifactory.stats(ARTIFACT_PATH)
    assert artifact_stats.dict() == ARTIFACT_STATS.dict()


@responses.activate
def test_copy_artifact_success():
    responses.add(
        responses.POST,
        f"{URL}/api/copy/{ARTIFACT_PATH}?to={ARTIFACT_NEW_PATH}&dry=0",
        status=200,
    )
    responses.add(
        responses.GET,
        f"{URL}/api/storage/{ARTIFACT_NEW_PATH}?properties[=x[,y]]",
        status=200,
        json=NEW_ARTIFACT_PROPERTIES.dict(),
    )

    artifactory = ArtifactoryArtifact(AuthModel(url=URL, auth=AUTH))
    artifact_copied = artifactory.copy(ARTIFACT_PATH, ARTIFACT_NEW_PATH)
    assert artifact_copied.dict() == NEW_ARTIFACT_PROPERTIES.dict()


@responses.activate
def test_move_artifact_success():
    responses.add(
        responses.POST,
        f"{URL}/api/move/{ARTIFACT_PATH}?to={ARTIFACT_NEW_PATH}&dry=0",
        status=200,
    )
    responses.add(
        responses.GET,
        f"{URL}/api/storage/{ARTIFACT_NEW_PATH}?properties[=x[,y]]",
        status=200,
        json=NEW_ARTIFACT_PROPERTIES.dict(),
    )

    artifactory = ArtifactoryArtifact(AuthModel(url=URL, auth=AUTH))
    artifact_moved = artifactory.move(ARTIFACT_PATH, ARTIFACT_NEW_PATH)
    assert artifact_moved.dict() == NEW_ARTIFACT_PROPERTIES.dict()


@responses.activate
def test_delete_artifact_success():
    responses.add(responses.DELETE, f"{URL}/{ARTIFACT_PATH}", status=200)

    artifactory = ArtifactoryArtifact(AuthModel(url=URL, auth=AUTH))
    artifactory.delete(ARTIFACT_PATH)
