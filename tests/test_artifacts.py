from __future__ import annotations

import urllib.parse
from pathlib import Path

import pytest
import responses

from pyartifactory import ArtifactoryArtifact
from pyartifactory.exception import ArtifactNotFoundError, ArtifactoryError, BadPropertiesError, PropertyNotFoundError
from pyartifactory.models import ArtifactPropertiesResponse, ArtifactStatsResponse, AuthModel
from pyartifactory.models.artifact import (
    ArtifactFileInfoResponse,
    ArtifactFolderInfoResponse,
    ArtifactListFileResponse,
    ArtifactListFolderResponse,
    ArtifactListResponse,
    Checksums,
)

URL = "http://localhost:8080/artifactory"
AUTH = ("user", "password_or_apiKey")
ARTIFACT_REPO = "my_repository"
ARTIFACT_PATH = f"{ARTIFACT_REPO}/file.txt"
ARTIFACT_NEW_PATH = "my-second-repository/file.txt"
ARTIFACT_SHORT_PATH = "/file.txt"
NX_ARTIFACT_PATH = f"{ARTIFACT_REPO}/nx_file.txt"
LOCAL_FILE_LOCATION = "tests/test_artifacts.py"
ARTIFACT_ONE_PROPERTY = ArtifactPropertiesResponse(
    uri=f"{URL}/api/storage/{ARTIFACT_PATH}",
    properties={"prop1": ["value"]},
)
ARTIFACT_MULTIPLE_PROPERTIES = ArtifactPropertiesResponse(
    uri=f"{URL}/api/storage/{ARTIFACT_PATH}",
    properties={"prop1": ["value"], "prop2": ["another value", "with multiple parts"]},
)
BAD_PROPERTY_NAME = "prop_with_bad_value"
BAD_PROPERTY_VALUE = "BAD_VALUE_(]!"
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
        "sha1": "962c287c760e03b03c17eb920f5358d05f44dd3b",
        "md5": "4cf609e0fe1267df8815bc650f5851e9",
        "sha256": "396cf16e8ce000342c95ffc7feb2a15701d0994b70c1b13fea7112f85ac8e858",
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

LIST_ARTIFACTS_RESPONSE = {
    "uri": f"{URL}/api/storage/{ARTIFACT_REPO}",
    "created": "2019-06-06T13:19:14.514Z",
    "files": [
        {
            "uri": "/archived",
            "size": -1,
            "lastModified": "2019-06-06T13:19:14.514Z",
            "folder": True,
        },
        {
            "uri": "/doc.txt",
            "size": 253207,
            "lastModified": "2019-06-06T13:19:14.514Z",
            "folder": False,
            "sha1": "962c287c760e03b03c17eb920f5358d05f44dd3b",
        },
        {
            "uri": "/archived/doc1.txt",
            "size": 253100,
            "lastModified": "2019-06-06T13:19:14.514Z",
            "folder": False,
            "sha1": "542c287c760e03b03c17eb920f5358d05f44dd3b",
        },
    ],
}
LIST_ARTIFACTS = ArtifactListResponse(**LIST_ARTIFACTS_RESPONSE)

ARTIFACT_STATS = ArtifactStatsResponse(
    uri="my_uri",
    downloadCount=0,
    lastDownloaded=0,
    remoteDownloadCount=0,
    remoteLastDownloaded=0,
)

CURRENT_FOLDER = Path(__file__).parent


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

    assert artifact.model_dump() == FOLDER_INFO.model_dump()


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
    assert artifact.model_dump() == FILE_INFO.model_dump()


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
    artifact = artifactory.deploy(Path(LOCAL_FILE_LOCATION), Path(ARTIFACT_PATH))

    artifactory.info.assert_called_once_with(Path(ARTIFACT_PATH))
    assert artifact.model_dump() == FILE_INFO.model_dump()


@responses.activate
def test_download_artifact_success(tmp_path):
    artifact_name = ARTIFACT_PATH.split("/")[1]
    responses.add(
        responses.GET,
        f"{URL}/api/storage/{ARTIFACT_PATH}",
        status=200,
        json=FILE_INFO_RESPONSE,
    )
    responses.add(responses.GET, f"{URL}/{ARTIFACT_PATH}", json=artifact_name, status=200)

    artifactory = ArtifactoryArtifact(AuthModel(url=URL, auth=AUTH))
    artifact = artifactory.download(ARTIFACT_PATH, str(tmp_path.resolve()))

    assert artifact.as_posix() == f"{tmp_path.as_posix()}/{artifact_name}"
    assert artifact.is_file()


@responses.activate
def test_stream_artifact_success():
    artifact_name = ARTIFACT_PATH.split("/")[1]
    responses.add(
        responses.GET,
        f"{URL}/api/storage/{ARTIFACT_PATH}",
        status=200,
        json=FILE_INFO_RESPONSE,
    )
    responses.add(responses.GET, f"{URL}/{ARTIFACT_PATH}", json=artifact_name, status=200)

    artifactory = ArtifactoryArtifact(AuthModel(url=URL, auth=AUTH))
    artifact_stream = artifactory.stream(ARTIFACT_PATH)

    text = bytearray()
    for chunk in artifact_stream:
        text.extend(chunk)

    assert len(text) == len(f'"{artifact_name}"'.encode("utf-8"))


@pytest.mark.parametrize(
    "requested_path",
    [ARTIFACT_REPO, f"{ARTIFACT_REPO}/", f"/{ARTIFACT_REPO}", f"/{ARTIFACT_REPO}/"],
)
@responses.activate
def test_download_folder_success(tmp_path, requested_path):
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
    responses.add(responses.GET, f"{URL}/{ARTIFACT_REPO}/child2", json="/child2", status=200)

    artifactory = ArtifactoryArtifact(AuthModel(url=URL, auth=AUTH))
    artifact = artifactory.download(requested_path, str(tmp_path.resolve()))

    assert artifact == Path(tmp_path.resolve() / ARTIFACT_REPO)
    assert (tmp_path / f"{ARTIFACT_REPO}" / "child1" / "grandchild").is_file()
    assert (tmp_path / f"{ARTIFACT_REPO}" / "child2").is_file()


@responses.activate
def test_get_artifact_single_property_success():
    responses.add(
        responses.GET,
        f"{URL}/api/storage/{ARTIFACT_PATH}?properties=prop1",
        json=ARTIFACT_ONE_PROPERTY.model_dump(),
        status=200,
    )

    artifactory = ArtifactoryArtifact(AuthModel(url=URL, auth=AUTH))
    artifact_properties = artifactory.properties(ARTIFACT_PATH, ["prop1"])
    assert artifact_properties.model_dump() == ARTIFACT_ONE_PROPERTY.model_dump()


@responses.activate
def test_get_artifact_multiple_properties_success():
    responses.add(
        responses.GET,
        f"{URL}/api/storage/{ARTIFACT_PATH}?properties=prop1,prop2",
        json=ARTIFACT_MULTIPLE_PROPERTIES.model_dump(),
        status=200,
    )

    artifactory = ArtifactoryArtifact(AuthModel(url=URL, auth=AUTH))
    artifact_properties = artifactory.properties(ARTIFACT_PATH, ["prop1", "prop2"])
    assert artifact_properties.model_dump() == ARTIFACT_MULTIPLE_PROPERTIES.model_dump()


@responses.activate
def test_get_artifact_multiple_properties_with_non_existing_properties_success():
    responses.add(
        responses.GET,
        f"{URL}/api/storage/{ARTIFACT_PATH}?properties=prop1,prop2,non_existing_prop",
        json=ARTIFACT_MULTIPLE_PROPERTIES.model_dump(),
        status=200,
    )

    artifactory = ArtifactoryArtifact(AuthModel(url=URL, auth=AUTH))
    artifact_properties = artifactory.properties(ARTIFACT_PATH, ["prop1", "prop2", "non_existing_prop"])
    assert artifact_properties.model_dump() == ARTIFACT_MULTIPLE_PROPERTIES.model_dump()


@responses.activate
def test_get_artifact_all_properties_success():
    responses.add(
        responses.GET,
        f"{URL}/api/storage/{ARTIFACT_PATH}?properties",
        json=ARTIFACT_MULTIPLE_PROPERTIES.model_dump(),
        status=200,
    )

    artifactory = ArtifactoryArtifact(AuthModel(url=URL, auth=AUTH))
    artifact_properties = artifactory.properties(ARTIFACT_PATH)
    assert artifact_properties.model_dump() == ARTIFACT_MULTIPLE_PROPERTIES.model_dump()


@responses.activate
def test_get_artifact_property_not_found_error():
    responses.add(
        responses.GET,
        f"{URL}/api/storage/{ARTIFACT_PATH}?properties=a_property_not_found",
        json={"errors": [{"status": 404, "message": "No properties could be found."}]},
        status=404,
    )

    artifactory = ArtifactoryArtifact(AuthModel(url=URL, auth=AUTH))
    with pytest.raises(PropertyNotFoundError):
        artifactory.properties(ARTIFACT_PATH, properties=["a_property_not_found"])


@responses.activate
def test_get_list_of_artifacts():
    responses.add(
        responses.GET,
        f"{URL}/api/storage/{ARTIFACT_REPO}?list&deep=1&listFolders=1",
        json=LIST_ARTIFACTS_RESPONSE,
        status=200,
    )

    artifactory = ArtifactoryArtifact(AuthModel(url=URL, auth=AUTH))
    artifact_list = artifactory.list(ARTIFACT_REPO)
    assert artifact_list.model_dump() == LIST_ARTIFACTS.model_dump()
    assert len(artifact_list.files) == 3
    assert isinstance(artifact_list.files[0], ArtifactListFolderResponse)
    assert isinstance(artifact_list.files[1], ArtifactListFileResponse)
    assert isinstance(artifact_list.files[2], ArtifactListFileResponse)


@responses.activate
def test_get_list_of_artifacts_not_found_error():
    responses.add(
        responses.GET,
        f"{URL}/api/storage/{ARTIFACT_REPO}?list&deep=1&listFolders=1",
        json={"errors": [{"status": 404, "message": "Artifact not found."}]},
        status=404,
    )

    artifactory = ArtifactoryArtifact(AuthModel(url=URL, auth=AUTH))
    with pytest.raises(ArtifactNotFoundError):
        artifactory.list(ARTIFACT_REPO)


@responses.activate
def test_get_artifact_stats_success():
    responses.add(
        responses.GET,
        f"{URL}/api/storage/{ARTIFACT_PATH}?stats",
        json=ARTIFACT_STATS.model_dump(),
        status=200,
    )

    artifactory = ArtifactoryArtifact(AuthModel(url=URL, auth=AUTH))
    artifact_stats = artifactory.stats(ARTIFACT_PATH)
    assert artifact_stats.model_dump() == ARTIFACT_STATS.model_dump()


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
    assert artifact_copied.model_dump() == FILE_INFO.model_dump()


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
    assert artifact_moved.model_dump() == FILE_INFO.model_dump()


@responses.activate
def test_delete_artifact_success():
    responses.add(responses.DELETE, f"{URL}/{ARTIFACT_PATH}", status=200)

    artifactory = ArtifactoryArtifact(AuthModel(url=URL, auth=AUTH))
    artifactory.delete(ARTIFACT_PATH)


@responses.activate
def test_set_property_success():
    properties_param_str = ""
    for k, v in ARTIFACT_MULTIPLE_PROPERTIES.properties.items():
        values_str = ",".join(v)
        properties_param_str += urllib.parse.quote_plus(f"{k}={values_str};")
    responses.add(
        responses.PUT,
        f"{URL}/api/storage/{ARTIFACT_PATH}?recursive=1&properties={properties_param_str.rstrip('%3B')}",
        status=200,
    )
    responses.add(
        responses.GET,
        f"{URL}/api/storage/{ARTIFACT_PATH}?properties=",
        json=ARTIFACT_MULTIPLE_PROPERTIES.model_dump(),
        status=200,
    )
    artifactory = ArtifactoryArtifact(AuthModel(url=URL, auth=AUTH))
    set_properties_response = artifactory.set_properties(ARTIFACT_PATH, ARTIFACT_MULTIPLE_PROPERTIES.properties)
    assert set_properties_response == ARTIFACT_MULTIPLE_PROPERTIES


@responses.activate
def test_deploy_artifact_with_properties_success():
    properties_param_str = ""
    for k, v in ARTIFACT_ONE_PROPERTY.properties.items():
        values_str = ",".join(v)
        properties_param_str += f"{k}={values_str};"
    responses.add(
        responses.PUT,
        f"{URL}/{ARTIFACT_PATH};{properties_param_str.rstrip(';')}",
        status=200,
    )
    responses.add(
        responses.GET,
        f"{URL}/api/storage/{ARTIFACT_PATH}",
        json=FILE_INFO_RESPONSE,
        status=200,
    )
    responses.add(
        responses.GET,
        f"{URL}/api/storage/{ARTIFACT_PATH}?properties=prop1",
        json=ARTIFACT_ONE_PROPERTY.model_dump(),
        status=200,
    )
    artifactory = ArtifactoryArtifact(AuthModel(url=URL, auth=AUTH))
    artifactory.deploy(
        Path(LOCAL_FILE_LOCATION),
        Path(ARTIFACT_PATH),
        properties=ARTIFACT_ONE_PROPERTY.properties,
        checksum_enabled=False,
    )
    artifact_properties = artifactory.properties(ARTIFACT_PATH, ["prop1"])
    assert artifact_properties.model_dump() == ARTIFACT_ONE_PROPERTY.model_dump()


@responses.activate
def test_deploy_artifact_with_multiple_properties_success():
    properties_param_str = ";".join(
        f"{k}={value}" for k, values in ARTIFACT_MULTIPLE_PROPERTIES.properties.items() for value in values
    )
    responses.add(
        responses.PUT,
        f"{URL}/{ARTIFACT_PATH};{properties_param_str.rstrip(';')}",
        status=200,
    )
    responses.add(
        responses.GET,
        f"{URL}/api/storage/{ARTIFACT_PATH}",
        json=FILE_INFO_RESPONSE,
        status=200,
    )
    responses.add(
        responses.GET,
        f"{URL}/api/storage/{ARTIFACT_PATH}?properties=prop1,prop2",
        json=ARTIFACT_MULTIPLE_PROPERTIES.model_dump(),
        status=200,
    )
    artifactory = ArtifactoryArtifact(AuthModel(url=URL, auth=AUTH))
    artifactory.deploy(
        Path(LOCAL_FILE_LOCATION),
        Path(ARTIFACT_PATH),
        properties=ARTIFACT_MULTIPLE_PROPERTIES.properties,
        checksum_enabled=False,
    )
    artifact_properties = artifactory.properties(ARTIFACT_PATH, ["prop1", "prop2"])
    assert artifact_properties.model_dump() == ARTIFACT_MULTIPLE_PROPERTIES.model_dump()


@responses.activate
def test_set_property_fail_artifact_not_found():
    properties_param_str = ""
    for k, v in ARTIFACT_ONE_PROPERTY.properties.items():
        values_str = ",".join(v)
        properties_param_str += urllib.parse.quote_plus(f"{k}={values_str};")
    responses.add(
        responses.PUT,
        f"{URL}/api/storage/{NX_ARTIFACT_PATH}?recursive=1&properties={properties_param_str.rstrip('%3B')}",
        status=404,
    )
    artifactory = ArtifactoryArtifact(AuthModel(url=URL, auth=AUTH))
    with pytest.raises(ArtifactNotFoundError):
        set_property_response = artifactory.set_properties(NX_ARTIFACT_PATH, ARTIFACT_ONE_PROPERTY.properties)
        assert set_property_response is None


@responses.activate
def test_set_property_fail_bad_value():
    properties_param_str = urllib.parse.quote_plus(f"{BAD_PROPERTY_NAME}={BAD_PROPERTY_VALUE}")
    responses.add(
        responses.PUT,
        f"{URL}/api/storage/{ARTIFACT_PATH}?recursive=1&properties={properties_param_str}",
        status=400,
    )
    artifactory = ArtifactoryArtifact(AuthModel(url=URL, auth=AUTH))
    with pytest.raises(BadPropertiesError):
        set_property_response = artifactory.set_properties(ARTIFACT_PATH, {BAD_PROPERTY_NAME: [BAD_PROPERTY_VALUE]})
        assert set_property_response is None


@responses.activate
def test_update_property_success():
    responses.add(
        responses.PATCH,
        f"{URL}/api/metadata/{ARTIFACT_PATH}?recursiveProperties=1",
        match=[responses.matchers.json_params_matcher({"props": ARTIFACT_MULTIPLE_PROPERTIES.properties})],
        status=200,
    )
    responses.add(
        responses.GET,
        f"{URL}/api/storage/{ARTIFACT_PATH}?properties=",
        json=ARTIFACT_MULTIPLE_PROPERTIES.model_dump(),
        status=200,
    )
    artifactory = ArtifactoryArtifact(AuthModel(url=URL, auth=AUTH))
    update_properties_response = artifactory.update_properties(ARTIFACT_PATH, ARTIFACT_MULTIPLE_PROPERTIES.properties)
    assert update_properties_response == ARTIFACT_MULTIPLE_PROPERTIES


@responses.activate
def test_update_property_fail_artifact_not_found():
    responses.add(
        responses.PATCH,
        f"{URL}/api/metadata/{NX_ARTIFACT_PATH}?recursiveProperties=1",
        match=[responses.matchers.json_params_matcher({"props": ARTIFACT_ONE_PROPERTY.properties})],
        status=400,
    )
    artifactory = ArtifactoryArtifact(AuthModel(url=URL, auth=AUTH))
    with pytest.raises(ArtifactoryError):
        update_properties_response = artifactory.update_properties(NX_ARTIFACT_PATH, ARTIFACT_ONE_PROPERTY.properties)
        assert update_properties_response is None


@responses.activate
def test_update_property_fail_bad_value():
    responses.add(
        responses.PATCH,
        f"{URL}/api/metadata/{ARTIFACT_PATH}?recursiveProperties=1",
        match=[responses.matchers.json_params_matcher({"props": {BAD_PROPERTY_NAME: [BAD_PROPERTY_VALUE]}})],
        status=400,
    )
    artifactory = ArtifactoryArtifact(AuthModel(url=URL, auth=AUTH))
    with pytest.raises(ArtifactoryError):
        update_properties_response = artifactory.update_properties(
            ARTIFACT_PATH,
            {BAD_PROPERTY_NAME: [BAD_PROPERTY_VALUE]},
        )
        assert update_properties_response is None


@pytest.mark.parametrize(
    "file_path,expected_sha1,expected_md5,expected_sha256",
    [
        pytest.param(
            CURRENT_FOLDER / "./resources/used_for_integration_tests.txt",
            "6eadcc38199835325cad99d2049749aa3b2ab5d1",
            "df3929d7b575b92fef7a97d2a7827c36",
            "f1d3f5f25ae31e46d13ce7b3e224158da45de2d0db388a693b08ec5cf0302227",
            id="used_for_integration_tests.txt",
        ),
        pytest.param(
            CURRENT_FOLDER / "./resources/empty_file.txt",
            "da39a3ee5e6b4b0d3255bfef95601890afd80709",
            "d41d8cd98f00b204e9800998ecf8427e",
            "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
            id="empty_file.txt",
        ),
        pytest.param(
            CURRENT_FOLDER / "./resources/picture-dog.jpg",
            "c3e7b4a20b35a87762f1844c7b961de668b58749",
            "1c9703e4a52b48892346a65b0356069b",
            "b7e8ca95bd76cedc161cb54bca1711a1fe495e1799e060acf10b7f5a7cfe6b29",
            id="picture-dog",
        ),
    ],
)
def test_checksum_defined_file(file_path: Path, expected_sha1: str, expected_md5: str, expected_sha256: str):
    result = Checksums.generate(file_path)
    expected = Checksums(
        sha1=expected_sha1,
        md5=expected_md5,
        sha256=expected_sha256,
    )
    assert result == expected


def test_get_hasher_security_flag():
    calls = {"kwargs": None}

    class Dummy:
        def __init__(self):
            self._buf = b""

        def update(self, b):
            self._buf += b

        def hexdigest(self):
            return "ok"

    def func(**kwargs):
        calls["kwargs"] = kwargs
        return Dummy()

    hasher = Checksums.get_hasher(func)
    assert isinstance(hasher, Dummy)
    assert calls["kwargs"] == {"usedforsecurity": False}


def test_get_hasher_type_error_thrown():
    calls = {"with_kwargs": 0, "without_kwargs": 0}

    class Dummy:
        def __init__(self):
            self._buf = b""

        def update(self, b):
            self._buf += b

        def hexdigest(self):
            return "ok"

    def func(**kwargs):
        if kwargs:
            calls["with_kwargs"] += 1
            raise TypeError("unexpected kwarg")
        calls["without_kwargs"] += 1
        return Dummy()

    hasher = Checksums.get_hasher(func)
    assert isinstance(hasher, Dummy)
    assert calls["with_kwargs"] == 1
    assert calls["without_kwargs"] == 1


@responses.activate
def test_deploy_artifact_with_checksum_success(mocker):
    responses.add(responses.PUT, f"{URL}/{ARTIFACT_PATH}", status=200)

    responses.add(
        responses.GET,
        f"{URL}/api/storage/{ARTIFACT_PATH}",
        json=FILE_INFO_RESPONSE,
        status=200,
    )
    artifactory = ArtifactoryArtifact(AuthModel(url=URL, auth=AUTH))
    mocker.spy(artifactory, "info")
    artifact = artifactory.deploy(Path(LOCAL_FILE_LOCATION), Path(ARTIFACT_PATH), checksum_enabled=True)

    artifactory.info.assert_called_once_with(Path(ARTIFACT_PATH))
    assert artifact.model_dump() == FILE_INFO.model_dump()


@responses.activate
def test_deploy_artifact_with_checksum_error_404():
    responses.add(responses.PUT, f"{URL}/{ARTIFACT_PATH}", status=404)

    with pytest.raises(ArtifactNotFoundError):
        artifactory = ArtifactoryArtifact(AuthModel(url=URL, auth=AUTH))
        artifactory.deploy(Path(LOCAL_FILE_LOCATION), Path(ARTIFACT_PATH), checksum_enabled=True)


@responses.activate
def test_deploy_artifact_with_checksum_error_but_other_than_404():
    responses.add(responses.PUT, f"{URL}/{ARTIFACT_PATH}", status=500)

    with pytest.raises(ArtifactoryError):
        artifactory = ArtifactoryArtifact(AuthModel(url=URL, auth=AUTH))
        artifactory.deploy(Path(LOCAL_FILE_LOCATION), Path(ARTIFACT_PATH), checksum_enabled=True)
