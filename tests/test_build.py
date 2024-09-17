from __future__ import annotations

import pytest
import requests
import responses
from requests.models import Response

from pyartifactory import ArtifactoryBuild
from pyartifactory.exception import ArtifactoryError, BuildNotFoundError
from pyartifactory.models import (
    AuthModel,
    BuildCreateRequest,
    BuildDeleteRequest,
    BuildDiffResponse,
    BuildError,
    BuildInfo,
    BuildListResponse,
    BuildPromotionRequest,
    BuildPromotionResult,
    BuildProperties,
)

URL = "http://localhost:8080/artifactory"
AUTH = ("user", "password_or_apiKey")

BUILD_INFO = BuildInfo(uri=f"{URL}/api/build/build_name/number")
BUILD_LIST_RESPONSE = BuildListResponse(uri=f"{URL}/api/build")
BUILD_NOT_FOUND_ERROR = BuildError(errors=[{"status": 404, "message": "Not found"}])
BUILD_GENERIC_ERROR = BuildError(errors=[{"status": 500, "message": "Generic error"}])
BUILD_DIFF = BuildDiffResponse()
BUILD_PROMOTION_REQUEST = BuildPromotionRequest(sourceRepo="repo-abc", targetRepo="repo-def")
BUILD_PROMOTION_RESULT = BuildPromotionResult()
BUILD_DELETE_REQUEST = BuildDeleteRequest(buildName="build", buildNumbers=["abc", "123"])
BUILD_DELETE_ERROR = BuildError(errors=[{"status": 404, "message": "Not found"}])
BUILD_CREATE_REQUEST = BuildCreateRequest(name="a-build", number="build-xx", started="2014-09-30T12:00:19.893+0300")

NOT_FOUND_HTTP_RESPONSE = Response()
NOT_FOUND_HTTP_RESPONSE.status_code = 404
NOT_FOUND_HTTP_RESPONSE.reason = "Not Found"
NOT_FOUND_HTTP_RESPONSE._content = b'{"errors": [{"status": 404, "message": "Not found ... "}]}'
NOT_FOUND_HTTP_RESPONSE.encoding = "utf-8"
NOT_FOUND_HTTP_RESPONSE.url = "http://jfrog-server..."

NOT_FOUND_EXCEPTION_BODY = requests.exceptions.HTTPError(response=NOT_FOUND_HTTP_RESPONSE)


@responses.activate
def test_get_build_info_success(mocker):
    responses.add(
        responses.GET,
        f"{URL}/api/build/build_name/abc",
        json=BUILD_INFO.model_dump(),
        status=200,
    )

    artifactory_build = ArtifactoryBuild(AuthModel(url=URL, auth=AUTH))
    mocker.spy(artifactory_build, "get_build_info")
    get_build = artifactory_build.get_build_info("build_name", "abc")

    assert isinstance(get_build, BuildInfo)


@responses.activate
@pytest.mark.parametrize(
    "build_num,properties_input,expected_query,raised_exc",
    [
        ("11", BuildProperties(), "", BuildNotFoundError),
        ("11", BuildProperties(diff="43"), "?diff=43", BuildNotFoundError),
        ("11", BuildProperties(diff="43", started="2024-08"), "?diff=43&started=2024-08", BuildNotFoundError),
        ("11", BuildProperties(diff="abc"), "?diff=abc", ArtifactoryError),
        ("def", BuildProperties(diff="22"), "?diff=22", ArtifactoryError),
    ],
)
def test_get_build_info_errors(mocker, build_num, properties_input, expected_query, raised_exc):
    responses.add(
        responses.GET,
        f"{URL}/api/build/build_name/{build_num}{expected_query}",
        body=NOT_FOUND_EXCEPTION_BODY,
        status=404,
    )

    artifactory_build = ArtifactoryBuild(AuthModel(url=URL, auth=AUTH))
    mocker.spy(artifactory_build, "get_build_info")
    with pytest.raises(raised_exc):
        artifactory_build.get_build_info("build_name", build_num, properties=properties_input)


@responses.activate
@pytest.mark.parametrize(
    "error_model_dump,raised_exc",
    [
        (BUILD_NOT_FOUND_ERROR.model_dump(), BuildNotFoundError),
        (BUILD_GENERIC_ERROR.model_dump(), ArtifactoryError),
    ],
)
def test_get_build_info_response_error(mocker, error_model_dump, raised_exc):
    responses.add(responses.GET, f"{URL}/api/build/build_name/123", body=NOT_FOUND_EXCEPTION_BODY, status=200)

    artifactory_build = ArtifactoryBuild(AuthModel(url=URL, auth=AUTH))
    mocker.spy(artifactory_build, "get_build_info")
    with pytest.raises(raised_exc):
        artifactory_build.get_build_info("build_name", "123")


@responses.activate
def test_promote_build_success(mocker):
    responses.add(
        responses.GET,
        f"{URL}/api/build/build_proj/build_number",
        json=BUILD_INFO.model_dump(),
        status=200,
    )
    _promotion_request = BUILD_PROMOTION_REQUEST.model_dump()
    responses.add(
        responses.POST,
        f"{URL}/api/build/promote/build_proj/build_number",
        json=_promotion_request,
        status=200,
    )

    artifactory_build = ArtifactoryBuild(AuthModel(url=URL, auth=AUTH))
    mocker.spy(artifactory_build, "promote_build")
    build_promotion = artifactory_build.promote_build("build_proj", "build_number", BUILD_PROMOTION_REQUEST)

    assert isinstance(build_promotion, BuildPromotionResult)


@responses.activate
def test_promote_build_errors(mocker):
    responses.add(
        responses.GET,
        f"{URL}/api/build/build_name/build_123",
        body=NOT_FOUND_EXCEPTION_BODY,
        status=200,
    )

    artifactory_build = ArtifactoryBuild(AuthModel(url=URL, auth=AUTH))
    mocker.spy(artifactory_build, "promote_build")
    with pytest.raises(BuildNotFoundError):
        artifactory_build.promote_build("build_name", "build_123", BUILD_PROMOTION_REQUEST)


@responses.activate
def test_promote_build_error_not_exist(mocker):
    responses.add(responses.GET, f"{URL}/api/build/build_name/123", body=NOT_FOUND_EXCEPTION_BODY, status=200)

    artifactory_build = ArtifactoryBuild(AuthModel(url=URL, auth=AUTH))
    mocker.spy(artifactory_build, "promote_build")
    with pytest.raises(ArtifactoryError):
        artifactory_build.promote_build("build_name", "123", BUILD_PROMOTION_REQUEST)


@responses.activate
def test_list_build(mocker):
    responses.add(
        responses.GET,
        f"{URL}/api/build",
        json=BUILD_LIST_RESPONSE.model_dump(),
        status=200,
    )

    artifactory_build = ArtifactoryBuild(AuthModel(url=URL, auth=AUTH))
    mocker.spy(artifactory_build, "list")
    build_list = artifactory_build.list()

    assert isinstance(build_list, BuildListResponse)


@responses.activate
def test_delete_build_success(mocker):
    for _build_number in BUILD_DELETE_REQUEST.buildNumbers:
        responses.add(
            responses.GET,
            f"{URL}/api/build/{BUILD_DELETE_REQUEST.buildName}/{_build_number}",
            json=BUILD_INFO.model_dump(),
            status=200,
        )

    responses.add(responses.POST, f"{URL}/api/build/delete", json=BUILD_DELETE_REQUEST.model_dump(), status=200)

    artifactory_build = ArtifactoryBuild(AuthModel(url=URL, auth=AUTH))
    mocker.spy(artifactory_build, "delete")
    artifactory_build.delete(BUILD_DELETE_REQUEST)


@responses.activate
def test_delete_build_error_not_exist(mocker):
    responses.add(
        responses.GET,
        f"{URL}/api/build/{BUILD_DELETE_REQUEST.buildName}/{BUILD_DELETE_REQUEST.buildNumbers[0]}",
        json=BUILD_INFO.model_dump(),
        status=200,
    )
    responses.add(
        responses.GET,
        f"{URL}/api/build/{BUILD_DELETE_REQUEST.buildName}/{BUILD_DELETE_REQUEST.buildNumbers[-1]}",
        body=NOT_FOUND_EXCEPTION_BODY,
        status=200,
    )

    artifactory_build = ArtifactoryBuild(AuthModel(url=URL, auth=AUTH))
    mocker.spy(artifactory_build, "delete")
    with pytest.raises(ArtifactoryError):
        artifactory_build.delete(BUILD_DELETE_REQUEST)


@responses.activate
def test_rename_build_success(mocker):
    responses.add(responses.GET, f"{URL}/api/build/build_name", json=BUILD_INFO.model_dump(), status=200)
    responses.add(responses.POST, f"{URL}/api/build/rename/build_name?to=new_name", status=200)

    artifactory_build = ArtifactoryBuild(AuthModel(url=URL, auth=AUTH))
    mocker.spy(artifactory_build, "build_rename")
    artifactory_build.build_rename("build_name", "new_name")


@responses.activate
def test_rename_build_error_not_exist(mocker):
    responses.add(responses.GET, f"{URL}/api/build/build_name", json=BUILD_NOT_FOUND_ERROR.model_dump(), status=404)

    artifactory_build = ArtifactoryBuild(AuthModel(url=URL, auth=AUTH))
    mocker.spy(artifactory_build, "build_rename")
    with pytest.raises(BuildNotFoundError):
        artifactory_build.build_rename("build_name", "new_name")


@responses.activate
def test_build_diff_success(mocker):
    responses.add(responses.GET, f"{URL}/api/build/build_name/123?diff=456", json=BUILD_DIFF.model_dump(), status=200)

    artifactory_build = ArtifactoryBuild(AuthModel(url=URL, auth=AUTH))
    mocker.spy(artifactory_build, "build_diff")
    artifactory_build.build_diff("build_name", "123", "456")


@responses.activate
def test_create_build_success(mocker):
    responses.add(
        responses.GET,
        f"{URL}/api/build/{BUILD_CREATE_REQUEST.name}/{BUILD_CREATE_REQUEST.number}",
        body=NOT_FOUND_EXCEPTION_BODY,
        status=200,
    )
    responses.add(responses.PUT, f"{URL}/api/build", status=204)

    artifactory_build = ArtifactoryBuild(AuthModel(url=URL, auth=AUTH))
    mocker.spy(artifactory_build, "create_build")
    artifactory_build.create_build(BUILD_CREATE_REQUEST)


@responses.activate
def test_create_build_error_already_exist(mocker):
    responses.add(
        responses.GET,
        f"{URL}/api/build/{BUILD_CREATE_REQUEST.name}/{BUILD_CREATE_REQUEST.number}",
        json=BUILD_INFO.model_dump(),
        status=200,
    )

    artifactory_build = ArtifactoryBuild(AuthModel(url=URL, auth=AUTH))
    mocker.spy(artifactory_build, "create_build")
    with pytest.raises(ArtifactoryError):
        artifactory_build.create_build(BUILD_CREATE_REQUEST)


@responses.activate
def test_create_build_error_not_created(mocker):
    responses.add(
        responses.GET,
        f"{URL}/api/build/{BUILD_CREATE_REQUEST.name}/{BUILD_CREATE_REQUEST.number}",
        json=BUILD_NOT_FOUND_ERROR.model_dump(),
        status=404,
    )
    responses.add(responses.PUT, f"{URL}/api/build", json=BUILD_CREATE_REQUEST.model_dump(), status=200)

    artifactory_build = ArtifactoryBuild(AuthModel(url=URL, auth=AUTH))
    mocker.spy(artifactory_build, "create_build")
    with pytest.raises(ArtifactoryError):
        artifactory_build.create_build(BUILD_CREATE_REQUEST)
