import pytest
import responses

from pyartifactory import ArtifactoryGroup
from pyartifactory.exception import GroupNotFoundException, GroupAlreadyExistsException
from pyartifactory.models import AuthModel, PasswordModel, Group


URL = "http://localhost:8080/artifactory"
AUTH = ("user", "password_or_apiKey")
NEW_GROUP = Group(name="test_group", description="test_group")
PASSWORD = PasswordModel(password="test")


class TestGroup:
    @staticmethod
    @responses.activate
    def test_create_group_fail_if_group_already_exists(mocker):
        responses.add(
            responses.GET,
            f"{URL}/api/security/groups/{NEW_GROUP.name}",
            json=NEW_GROUP.dict(),
            status=200,
        )

        artifactory_group = ArtifactoryGroup(AuthModel(url=URL, auth=AUTH))
        mocker.spy(artifactory_group, "get")
        with pytest.raises(GroupAlreadyExistsException):
            artifactory_group.create(NEW_GROUP)

        artifactory_group.get.assert_called_once_with(NEW_GROUP.name)

    @staticmethod
    @responses.activate
    def test_create_group_success(mocker):
        responses.add(
            responses.GET,
            f"{URL}/api/security/groups/{NEW_GROUP.name}",
            json=NEW_GROUP.dict(),
            status=404,
        )
        responses.add(
            responses.PUT,
            f"{URL}/api/security/groups/{NEW_GROUP.name}",
            json=NEW_GROUP.dict(),
            status=201,
        )

        artifactory_group = ArtifactoryGroup(AuthModel(url=URL, auth=AUTH))
        mocker.spy(artifactory_group, "get")
        with pytest.raises(GroupNotFoundException):
            artifactory_group.create(NEW_GROUP)

        artifactory_group.get.assert_called_with(NEW_GROUP.name)
        assert artifactory_group.get.call_count == 2

    @staticmethod
    @responses.activate
    def test_get_group_error_not_found():
        responses.add(
            responses.GET, f"{URL}/api/security/groups/{NEW_GROUP.name}", status=404
        )

        artifactory_group = ArtifactoryGroup(AuthModel(url=URL, auth=AUTH))
        with pytest.raises(GroupNotFoundException):
            artifactory_group.get(NEW_GROUP.name)

    @staticmethod
    @responses.activate
    def test_get_group_success(mocker):
        responses.add(
            responses.GET,
            f"{URL}/api/security/groups/{NEW_GROUP.name}",
            json=NEW_GROUP.dict(),
            status=200,
        )

        artifactory_group = ArtifactoryGroup(AuthModel(url=URL, auth=AUTH))
        mocker.spy(artifactory_group, "get")
        artifactory_group.get(NEW_GROUP.name)

        artifactory_group.get.assert_called_with(NEW_GROUP.name)

    @staticmethod
    @responses.activate
    def test_list_group_success(mocker):
        responses.add(
            responses.GET,
            f"{URL}/api/security/groups",
            json=[NEW_GROUP.dict()],
            status=200,
        )

        artifactory_group = ArtifactoryGroup(AuthModel(url=URL, auth=AUTH))
        mocker.spy(artifactory_group, "list")
        artifactory_group.list()

        artifactory_group.list.assert_called_once()

    @staticmethod
    @responses.activate
    def test_update_group_fail_if_group_not_found(mocker):
        responses.add(
            responses.GET, f"{URL}/api/security/groups/{NEW_GROUP.name}", status=404
        )

        artifactory_group = ArtifactoryGroup(AuthModel(url=URL, auth=AUTH))
        mocker.spy(artifactory_group, "get")
        with pytest.raises(GroupNotFoundException):
            artifactory_group.update(NEW_GROUP)

        artifactory_group.get.assert_called_once_with(NEW_GROUP.name)

    @staticmethod
    @responses.activate
    def test_update_group_success(mocker):
        responses.add(
            responses.GET,
            f"{URL}/api/security/groups/{NEW_GROUP.name}",
            json=NEW_GROUP.dict(),
            status=200,
        )

        responses.add(
            responses.POST,
            f"{URL}/api/security/groups/{NEW_GROUP.name}",
            json=NEW_GROUP.dict(),
            status=200,
        )
        artifactory_group = ArtifactoryGroup(AuthModel(url=URL, auth=AUTH))
        mocker.spy(artifactory_group, "get")
        artifactory_group.update(NEW_GROUP)

        artifactory_group.get.assert_called_with(NEW_GROUP.name)
        assert artifactory_group.get.call_count == 2

    @staticmethod
    @responses.activate
    def test_delete_group_fail_if_group_not_found(mocker):
        responses.add(
            responses.GET, f"{URL}/api/security/groups/{NEW_GROUP.name}", status=404
        )

        artifactory_group = ArtifactoryGroup(AuthModel(url=URL, auth=AUTH))
        mocker.spy(artifactory_group, "get")

        with pytest.raises(GroupNotFoundException):
            artifactory_group.delete(NEW_GROUP.name)

        artifactory_group.get.assert_called_once_with(NEW_GROUP.name)

    @staticmethod
    @responses.activate
    def test_delete_group_success(mocker):
        responses.add(
            responses.GET,
            f"{URL}/api/security/groups/{NEW_GROUP.name}",
            json=NEW_GROUP.dict(),
            status=200,
        )

        responses.add(
            responses.DELETE, f"{URL}/api/security/groups/{NEW_GROUP.name}", status=204
        )
        artifactory_group = ArtifactoryGroup(AuthModel(url=URL, auth=AUTH))
        mocker.spy(artifactory_group, "get")
        artifactory_group.delete(NEW_GROUP.name)

        artifactory_group.get.assert_called_once_with(NEW_GROUP.name)
