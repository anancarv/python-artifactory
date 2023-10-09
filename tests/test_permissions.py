from __future__ import annotations

import pytest
import responses

from pyartifactory import ArtifactoryPermission
from pyartifactory.exception import PermissionAlreadyExistsError, PermissionNotFoundError
from pyartifactory.models.auth import AuthModel
from pyartifactory.models.permission import Permission, PermissionV2, SimplePermission

URL = "http://localhost:8080/artifactory"
AUTH = ("user", "password_or_apiKey")
API_URI = "api/security/permissions"
API_URI_V2 = "api/v2/security/permissions"
SIMPLE_PERMISSION = SimplePermission(name="test_permission", uri="someuri")
PERMISSION = Permission(
    **{
        "name": "test_permission",
        "repositories": ["test_repository"],
        "principals": {
            "users": {"test_user": ["r", "w", "n", "d"]},
            "groups": {"developers": ["r"]},
        },
    },
)
PERMISSIONV2 = PermissionV2(
    **{
        "name": "test_permission",
        "repo": {
            "include-patterns": ["**"],
            "exclude-patterns": [],
            "repositories": ["test_repository"],
            "actions": {
                "users": {"test_user": ["read", "annotate", "write", "delete"]},
                "groups": {"developers": ["read", "annotate", "write", "delete"]},
            },
        },
        "build": {
            "include-patterns": [""],
            "exclude-patterns": [""],
            "repositories": ["artifactory-build-info"],
            "actions": {
                "users": {"bob": ["read", "manage"], "alice": ["write"]},
                "groups": {
                    "dev-leads": ["manage", "read", "write", "annotate", "delete"],
                    "readers": ["read"],
                },
            },
        },
        "releaseBundle": {
            "include-patterns": ["**"],
            "exclude-patterns": [],
            "repositories": ["release-bundles"],
            "actions": {
                "users": {"user_name": ["read", "write"]},
                "groups": {"group_name": ["read", "write"]},
            },
        },
    },
)


@pytest.mark.parametrize(
    "api_version,permission,api_uri",
    [(1, PERMISSION, API_URI), (2, PERMISSIONV2, API_URI_V2)],
)
@responses.activate
def test_create_permission_fail_if_group_already_exists(mocker, api_version, permission, api_uri):
    responses.add(
        responses.GET,
        f"{URL}/{api_uri}/{permission.name}",
        json=permission.model_dump(),
        status=200,
    )

    artifactory_permission = ArtifactoryPermission(AuthModel(url=URL, auth=AUTH, api_version=api_version))
    mocker.spy(artifactory_permission, "get")
    with pytest.raises(PermissionAlreadyExistsError):
        artifactory_permission.create(permission)
    artifactory_permission.get.assert_called_once_with(permission.name)


@pytest.mark.parametrize(
    "api_version,permission,api_uri",
    [(1, PERMISSION, API_URI), (2, PERMISSIONV2, API_URI_V2)],
)
@responses.activate
def test_create_permission_success(mocker, api_version, permission, api_uri):
    responses.add(responses.GET, f"{URL}/{api_uri}/{permission.name}", status=404)
    responses.add(
        responses.PUT,
        f"{URL}/{api_uri}/{permission.name}",
        json=permission.model_dump(),
        status=201,
    )
    responses.add(
        responses.GET,
        f"{URL}/{api_uri}/{permission.name}",
        json=permission.model_dump(),
        status=200,
    )

    artifactory_permission = ArtifactoryPermission(AuthModel(url=URL, auth=AUTH, api_version=api_version))
    mocker.spy(artifactory_permission, "get")
    mocked_permission = artifactory_permission.create(permission)
    artifactory_permission.get.assert_called_with(permission.name)
    assert mocked_permission.model_dump() == permission.model_dump()

    assert artifactory_permission.get.call_count == 2


@pytest.mark.parametrize(
    "api_version,permission,api_uri",
    [(1, PERMISSION, API_URI), (2, PERMISSIONV2, API_URI_V2)],
)
@responses.activate
def test_get_permission_error_not_found(api_version, permission, api_uri):
    responses.add(responses.GET, f"{URL}/{api_uri}/{permission.name}", status=404)

    artifactory_permission = ArtifactoryPermission(AuthModel(url=URL, auth=AUTH, api_version=api_version))
    with pytest.raises(PermissionNotFoundError):
        artifactory_permission.get(permission.name)


@pytest.mark.parametrize(
    "api_version,permission,api_uri",
    [(1, PERMISSION, API_URI), (2, PERMISSIONV2, API_URI_V2)],
)
@responses.activate
def test_get_permission_success(mocker, api_version, permission, api_uri):
    responses.add(
        responses.GET,
        f"{URL}/{api_uri}/{permission.name}",
        json=permission.model_dump(),
        status=200,
    )

    artifactory_permission = ArtifactoryPermission(AuthModel(url=URL, auth=AUTH, api_version=api_version))
    mocker.spy(artifactory_permission, "get")
    mocked_permission = artifactory_permission.get(permission.name)
    artifactory_permission.get.assert_called_with(permission.name)

    assert mocked_permission.model_dump() == permission.model_dump()


@pytest.mark.parametrize("api_version,api_uri", [(1, API_URI), (2, API_URI_V2)])
@responses.activate
def test_list_group_success(mocker, api_version, api_uri):
    responses.add(
        responses.GET,
        f"{URL}/{api_uri}",
        json=[SIMPLE_PERMISSION.model_dump()],
        status=200,
    )

    artifactory_permission = ArtifactoryPermission(AuthModel(url=URL, auth=AUTH, api_version=api_version))
    mocker.spy(artifactory_permission, "list")
    permission_list = artifactory_permission.list()
    artifactory_permission.list.assert_called_once()
    assert permission_list == [SIMPLE_PERMISSION]


@pytest.mark.parametrize(
    "api_version,permission,api_uri",
    [(1, PERMISSION, API_URI), (2, PERMISSIONV2, API_URI_V2)],
)
@responses.activate
def test_delete_permission_fail_if_group_not_found(mocker, api_version, permission, api_uri):
    responses.add(responses.GET, f"{URL}/{api_uri}/{permission.name}", status=404)

    artifactory_permission = ArtifactoryPermission(AuthModel(url=URL, auth=AUTH, api_version=api_version))
    mocker.spy(artifactory_permission, "get")

    with pytest.raises(PermissionNotFoundError):
        artifactory_permission.delete(permission.name)

    artifactory_permission.get.assert_called_once_with(permission.name)


@pytest.mark.parametrize(
    "api_version,permission,api_uri",
    [(1, PERMISSION, API_URI), (2, PERMISSIONV2, API_URI_V2)],
)
@responses.activate
def test_delete_group_success(mocker, api_version, permission, api_uri):
    responses.add(
        responses.GET,
        f"{URL}/{api_uri}/{permission.name}",
        json=permission.model_dump(),
        status=200,
    )

    responses.add(
        responses.DELETE,
        f"{URL}/{api_uri}/{permission.name}",
        status=204,
    )
    artifactory_permission = ArtifactoryPermission(AuthModel(url=URL, auth=AUTH, api_version=api_version))
    mocker.spy(artifactory_permission, "get")
    artifactory_permission.delete(permission.name)

    artifactory_permission.get.assert_called_once_with(permission.name)
