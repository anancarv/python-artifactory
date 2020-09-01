import pytest
import responses

from pyartifactory import ArtifactoryArtifact
from pyartifactory.exception import PropertyNotFoundException
from pyartifactory.models import (
    ArtifactPropertiesResponse,
    ArtifactStatsResponse,
    AuthModel,
)
from pyartifactory.models.artifact import (
    ArtifactFolderInfoResponse,
    ArtifactFileInfoResponse,
)

URL = "http://localhost:8080/artifactory"
AUTH = ("user", "password_or_apiKey")
ARTIFACT_REPO = "my_repository"
ARTIFACT_PATH = f"{ARTIFACT_REPO}/file.txt"
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
FOLDER_INFO_RESPONSE = {
    "uri": f"{URL}/api/storage/{ARTIFACT_REPO}",
    "repo": ARTIFACT_REPO,
    "path": "/",
    "created": "2019-06-06T13:19:14.514Z",
    "createdBy": "userY",
    "lastModified": "2019-06-06T13:19:14.514Z",
    "modifiedBy": "userX",
    "lastUpdated": "2019-06-06T13:19:14.514Z",
    "children": [
        {"uri": "/child1", "folder": "true"},
        {"uri": "/child2", "folder": "false"},
    ],
}
FOLDER_INFO = ArtifactFolderInfoResponse(**FOLDER_INFO_RESPONSE)

CHILD1_FOLDER_INFO_RESPONSE = FOLDER_INFO_RESPONSE.copy()
CHILD1_FOLDER_INFO_RESPONSE["uri"] = f"{URL}/api/storage/{ARTIFACT_REPO}/child1"
CHILD1_FOLDER_INFO_RESPONSE["path"] = "/child1"
CHILD1_FOLDER_INFO_RESPONSE["children"] = [
    {"uri": "/grandchild", "folder": "false"},
]
CHILD1_FOLDER_INFO = ArtifactFolderInfoResponse(**CHILD1_FOLDER_INFO_RESPONSE)


FILE_INFO_RESPONSE = {
    "repo": ARTIFACT_REPO,
    "path": ARTIFACT_SHORT_PATH,
    "created": "2019-06-06T13:19:14.514Z",
    "createdBy": "userY",
    "lastModified": "2019-06-06T13:19:14.514Z",
    "modifiedBy": "userX",
    "lastUpdated": "2019-06-06T13:19:14.514Z",
    "downloadUri": f"{URL}/api/storage/{ARTIFACT_PATH}",
    "mimeType": "application/json",
    "size": "3454",
    "checksums": {
        "sha1": "962c287c760e03b03c17eb920f5358d05f44dd3b",
        "md5": "4cf609e0fe1267df8815bc650f5851e9",
        "sha256": "396cf16e8ce000342c95ffc7feb2a15701d0994b70c1b13fea7112f85ac8e858",
    },
    "originalChecksums": {
        "sha256": "396cf16e8ce000342c95ffc7feb2a15701d0994b70c1b13fea7112f85ac8e858"
    },
    "uri": f"{URL}/api/storage/{ARTIFACT_PATH}",
}
FILE_INFO = ArtifactFileInfoResponse(**FILE_INFO_RESPONSE)

CHILD2_INFO_RESPONSE = FILE_INFO_RESPONSE.copy()
CHILD2_INFO_RESPONSE["uri"] = f"{URL}/api/storage/{ARTIFACT_REPO}/child2"
CHILD2_INFO_RESPONSE["path"] = "/child2"
CHILD2_FILE_INFO = ArtifactFileInfoResponse(**CHILD2_INFO_RESPONSE)

GRANDCHILD_INFO_RESPONSE = FILE_INFO_RESPONSE.copy()
GRANDCHILD_INFO_RESPONSE["uri"] = f"{URL}/api/storage/{ARTIFACT_REPO}/child1/grandchild"
GRANDCHILD_INFO_RESPONSE["path"] = "/child1/grandchild"
GRANDCHILD_FILE_INFO = ArtifactFileInfoResponse(**GRANDCHILD_INFO_RESPONSE)


ARTIFACT_STATS = ArtifactStatsResponse(
    uri="my_uri",
    downloadCount=0,
    lastDownloaded=0,
    remoteDownloadCount=0,
    remoteLastDownloaded=0,
)


@responses.activate
def test_get_artifact_folder_info_success():
    responses.add(
        responses.GET,
        f"{URL}/api/storage/{ARTIFACT_REPO}",
        status=200,
        json=FOLDER_INFO_RESPONSE,
    )
    artifactory = ArtifactoryArtifact(AuthModel(url=URL, auth=AUTH))
    artifact = artifactory.info(ARTIFACT_REPO)
    assert isinstance(artifact, ArtifactFolderInfoResponse)
    assert artifact.dict() == FOLDER_INFO.dict()


@responses.activate
def test_get_artifact_file_info_success():
    responses.add(
        responses.GET,
        f"{URL}/api/storage/{ARTIFACT_PATH}",
        status=200,
        json=FILE_INFO_RESPONSE,
    )
    artifactory = ArtifactoryArtifact(AuthModel(url=URL, auth=AUTH))
    artifact = artifactory.info(ARTIFACT_PATH)
    assert artifact.dict() == FILE_INFO.dict()


@responses.activate
def test_deploy_artifact_success(mocker):
    responses.add(responses.PUT, f"{URL}/{ARTIFACT_PATH}", status=200)

    responses.add(
        responses.GET,
        f"{URL}/api/storage/{ARTIFACT_PATH}",
        json=FILE_INFO_RESPONSE,
        status=200,
    )
    artifactory = ArtifactoryArtifact(AuthModel(url=URL, auth=AUTH))
    mocker.spy(artifactory, "info")
    artifact = artifactory.deploy(LOCAL_FILE_LOCATION, ARTIFACT_PATH)

    artifactory.info.assert_called_once_with(ARTIFACT_PATH)
    assert artifact.dict() == FILE_INFO.dict()


@responses.activate
def test_download_artifact_success(tmp_path):
    artifact_name = ARTIFACT_PATH.split("/")[1]
    responses.add(
        responses.GET,
        f"{URL}/api/storage/{ARTIFACT_PATH}",
        status=200,
        json=FILE_INFO_RESPONSE,
    )
    responses.add(
        responses.GET, f"{URL}/{ARTIFACT_PATH}", json=artifact_name, status=200
    )

    artifactory = ArtifactoryArtifact(AuthModel(url=URL, auth=AUTH))
    artifact = artifactory.download(ARTIFACT_PATH, str(tmp_path.resolve()))

    assert artifact == f"{tmp_path.resolve()}/{artifact_name}"
    assert (tmp_path / artifact_name).is_file()


@responses.activate
def test_download_folder_success(tmp_path):
    # artifact_name = ARTIFACT_PATH.split("/")[1]
    responses.add(
        responses.GET,
        f"{URL}/api/storage/{ARTIFACT_REPO}",
        status=200,
        json=FOLDER_INFO_RESPONSE,
    )
    responses.add(
        responses.GET,
        f"{URL}/api/storage/{ARTIFACT_REPO}/child1",
        status=200,
        json=CHILD1_FOLDER_INFO_RESPONSE,
    )
    responses.add(
        responses.GET,
        f"{URL}/api/storage/{ARTIFACT_REPO}/child2",
        status=200,
        json=CHILD2_INFO_RESPONSE,
    )
    responses.add(
        responses.GET,
        f"{URL}/api/storage/{ARTIFACT_REPO}/child1/grandchild",
        status=200,
        json=GRANDCHILD_INFO_RESPONSE,
    )
    responses.add(responses.GET, f"{URL}/{ARTIFACT_REPO}", json="/", status=200)
    responses.add(
        responses.GET,
        f"{URL}/{ARTIFACT_REPO}/child1/grandchild",
        json="/child1/grandchild",
        status=200,
    )
    responses.add(
        responses.GET, f"{URL}/{ARTIFACT_REPO}/child2", json="/child2", status=200
    )

    artifactory = ArtifactoryArtifact(AuthModel(url=URL, auth=AUTH))
    artifact = artifactory.download(f"{ARTIFACT_REPO}/", str(tmp_path.resolve()))

    assert artifact == f"{tmp_path.resolve()}/{ARTIFACT_REPO}"
    assert (tmp_path / f"{ARTIFACT_REPO}" / "child1" / "grandchild").is_file()
    assert (tmp_path / f"{ARTIFACT_REPO}" / "child2").is_file()


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
        f"{URL}/api/storage/{ARTIFACT_NEW_PATH}",
        status=200,
        json=FILE_INFO_RESPONSE,
    )

    artifactory = ArtifactoryArtifact(AuthModel(url=URL, auth=AUTH))
    artifact_copied = artifactory.copy(ARTIFACT_PATH, ARTIFACT_NEW_PATH)
    assert artifact_copied.dict() == FILE_INFO.dict()


@responses.activate
def test_move_artifact_success():
    responses.add(
        responses.POST,
        f"{URL}/api/move/{ARTIFACT_PATH}?to={ARTIFACT_NEW_PATH}&dry=0",
        status=200,
    )
    responses.add(
        responses.GET,
        f"{URL}/api/storage/{ARTIFACT_NEW_PATH}",
        status=200,
        json=FILE_INFO_RESPONSE,
    )

    artifactory = ArtifactoryArtifact(AuthModel(url=URL, auth=AUTH))
    artifact_moved = artifactory.move(ARTIFACT_PATH, ARTIFACT_NEW_PATH)
    assert artifact_moved.dict() == FILE_INFO.dict()


@responses.activate
def test_delete_artifact_success():
    responses.add(responses.DELETE, f"{URL}/{ARTIFACT_PATH}", status=200)

    artifactory = ArtifactoryArtifact(AuthModel(url=URL, auth=AUTH))
    artifactory.delete(ARTIFACT_PATH)
