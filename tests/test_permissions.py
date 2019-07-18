import pytest
import responses

from pyartifactory import ArtifactoryPermission
from pyartifactory.exception import (
    PermissionNotFoundException,
    PermissionAlreadyExistsException,
)
from pyartifactory.models.Auth import AuthModel
from pyartifactory.models.Permission import Permission, SimplePermission

URL = "http://localhost:8080/artifactory"
AUTH = ("user", "password_or_apiKey")

SIMPLE_PERMISSION = SimplePermission(name="test_permission", uri="someuri")
PERMISSION = Permission(
    **{
        "name": "test_permission",
        "repositories": ["test_repository"],
        "principals": {
            "users": {"test_user": ["r", "w", "n", "d"]},
            "groups": {"developers": ["r"]},
        },
    }
)


class TestPermission:
    @staticmethod
    @responses.activate
    def test_create_permission_fail_if_group_already_exists(mocker):
        responses.add(
            responses.GET,
            f"{URL}/api/security/permissions/{PERMISSION.name}",
            json=PERMISSION.dict(),
            status=200,
        )

        artifactory_permission = ArtifactoryPermission(AuthModel(url=URL, auth=AUTH))
        mocker.spy(artifactory_permission, "get")
        with pytest.raises(PermissionAlreadyExistsException):
            permission = artifactory_permission.create(PERMISSION)
            artifactory_permission.get.assert_called_once_with(PERMISSION.name)
            assert permission == PERMISSION.dict()

    @staticmethod
    @responses.activate
    def test_create_permission_success(mocker):
        responses.add(
            responses.GET,
            f"{URL}/api/security/permissions/{PERMISSION.name}",
            status=404,
        )
        responses.add(
            responses.PUT,
            f"{URL}/api/security/permissions/{PERMISSION.name}",
            json=PERMISSION.dict(),
            status=201,
        )
        responses.add(
            responses.GET,
            f"{URL}/api/security/permissions/{PERMISSION.name}",
            json=PERMISSION.dict(),
            status=200,
        )

        artifactory_permission = ArtifactoryPermission(AuthModel(url=URL, auth=AUTH))
        mocker.spy(artifactory_permission, "get")
        permission = artifactory_permission.create(PERMISSION)
        artifactory_permission.get.assert_called_with(PERMISSION.name)
        assert permission == PERMISSION.dict()

        assert artifactory_permission.get.call_count == 2

    @staticmethod
    @responses.activate
    def test_get_permission_error_not_found():
        responses.add(
            responses.GET,
            f"{URL}/api/security/permissions/{PERMISSION.name}",
            status=404,
        )

        artifactory_permission = ArtifactoryPermission(AuthModel(url=URL, auth=AUTH))
        with pytest.raises(PermissionNotFoundException):
            artifactory_permission.get(PERMISSION.name)

    @staticmethod
    @responses.activate
    def test_get_permission_success(mocker):
        responses.add(
            responses.GET,
            f"{URL}/api/security/permissions/{PERMISSION.name}",
            json=PERMISSION.dict(),
            status=200,
        )

        artifactory_permission = ArtifactoryPermission(AuthModel(url=URL, auth=AUTH))
        mocker.spy(artifactory_permission, "get")
        permission = artifactory_permission.get(PERMISSION.name)
        artifactory_permission.get.assert_called_with(PERMISSION.name)

        assert permission == PERMISSION.dict()

    @staticmethod
    @responses.activate
    def test_list_group_success(mocker):
        responses.add(
            responses.GET,
            f"{URL}/api/security/permissions",
            json=[SIMPLE_PERMISSION.dict()],
            status=200,
        )

        artifactory_permission = ArtifactoryPermission(AuthModel(url=URL, auth=AUTH))
        mocker.spy(artifactory_permission, "list")
        permission_list = artifactory_permission.list()
        artifactory_permission.list.assert_called_once()

        assert permission_list == [SIMPLE_PERMISSION.dict()]

    @staticmethod
    @responses.activate
    def test_delete_permission_fail_if_group_not_found(mocker):
        responses.add(
            responses.GET,
            f"{URL}/api/security/permissions/{PERMISSION.name}",
            status=404,
        )

        artifactory_permission = ArtifactoryPermission(AuthModel(url=URL, auth=AUTH))
        mocker.spy(artifactory_permission, "get")

        with pytest.raises(PermissionNotFoundException):
            artifactory_permission.delete(PERMISSION.name)

        artifactory_permission.get.assert_called_once_with(PERMISSION.name)

    @staticmethod
    @responses.activate
    def test_delete_group_success(mocker):
        responses.add(
            responses.GET,
            f"{URL}/api/security/permissions/{PERMISSION.name}",
            json=PERMISSION.dict(),
            status=200,
        )

        responses.add(
            responses.DELETE,
            f"{URL}/api/security/permissions/{PERMISSION.name}",
            status=204,
        )
        artifactory_permission = ArtifactoryPermission(AuthModel(url=URL, auth=AUTH))
        mocker.spy(artifactory_permission, "get")
        artifactory_permission.delete(PERMISSION.name)

        artifactory_permission.get.assert_called_once_with(PERMISSION.name)
