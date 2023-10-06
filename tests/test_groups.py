from __future__ import annotations

import pytest
import responses

from pyartifactory import ArtifactoryGroup
from pyartifactory.exception import GroupAlreadyExistsError, GroupNotFoundError
from pyartifactory.models import AuthModel, Group, PasswordModel

URL = "http://localhost:8080/artifactory"
AUTH = ("user", "password_or_apiKey")
NEW_GROUP = Group(name="test_group", description="test_group")
GROUP_WITH_USERS = Group(name="test_group", userNames=["user1", "user2"])
PASSWORD = PasswordModel(password="test")


@responses.activate
def test_create_group_fail_if_group_already_exists(mocker):
    responses.add(
        responses.GET,
        f"{URL}/api/security/groups/{NEW_GROUP.name}",
        json=NEW_GROUP.model_dump(),
        status=200,
    )

    artifactory_group = ArtifactoryGroup(AuthModel(url=URL, auth=AUTH))
    mocker.spy(artifactory_group, "get")
    with pytest.raises(GroupAlreadyExistsError):
        artifactory_group.create(NEW_GROUP)

    artifactory_group.get.assert_called_once_with(NEW_GROUP.name)


@responses.activate
def test_create_group_success(mocker):
    responses.add(responses.GET, f"{URL}/api/security/groups/{NEW_GROUP.name}", status=404)
    responses.add(
        responses.PUT,
        f"{URL}/api/security/groups/{NEW_GROUP.name}",
        json=NEW_GROUP.model_dump(),
        status=201,
    )
    responses.add(
        responses.GET,
        f"{URL}/api/security/groups/{NEW_GROUP.name}",
        json=NEW_GROUP.model_dump(),
        status=200,
    )

    artifactory_group = ArtifactoryGroup(AuthModel(url=URL, auth=AUTH))
    mocker.spy(artifactory_group, "get")
    group: Group = artifactory_group.create(NEW_GROUP)

    artifactory_group.get.assert_called_with(NEW_GROUP.name)
    assert artifactory_group.get.call_count == 2
    assert group.model_dump() == NEW_GROUP.model_dump()


@responses.activate
def test_get_group_error_not_found():
    responses.add(responses.GET, f"{URL}/api/security/groups/{NEW_GROUP.name}", status=404)

    artifactory_group = ArtifactoryGroup(AuthModel(url=URL, auth=AUTH))
    with pytest.raises(GroupNotFoundError):
        artifactory_group.get(NEW_GROUP.name)


@responses.activate
def test_get_group_success(mocker):
    responses.add(
        responses.GET,
        f"{URL}/api/security/groups/{NEW_GROUP.name}?includeUsers=True",
        json=GROUP_WITH_USERS.model_dump(),
        status=200,
    )

    artifactory_group = ArtifactoryGroup(AuthModel(url=URL, auth=AUTH))
    mocker.spy(artifactory_group, "get")
    group = artifactory_group.get(NEW_GROUP.name)

    assert group.model_dump() == GROUP_WITH_USERS.model_dump()


@responses.activate
def test_list_group_success(mocker):
    responses.add(
        responses.GET,
        f"{URL}/api/security/groups",
        json=[NEW_GROUP.model_dump()],
        status=200,
    )

    artifactory_group = ArtifactoryGroup(AuthModel(url=URL, auth=AUTH))
    mocker.spy(artifactory_group, "list_all")
    artifactory_group.list_all()

    artifactory_group.list_all.assert_called_once()


@responses.activate
def test_update_group_fail_if_group_not_found(mocker):
    responses.add(responses.GET, f"{URL}/api/security/groups/{NEW_GROUP.name}", status=404)

    artifactory_group = ArtifactoryGroup(AuthModel(url=URL, auth=AUTH))
    mocker.spy(artifactory_group, "get")
    with pytest.raises(GroupNotFoundError):
        artifactory_group.update(NEW_GROUP)

    artifactory_group.get.assert_called_once_with(NEW_GROUP.name)


@responses.activate
def test_update_group_success(mocker):
    responses.add(
        responses.GET,
        f"{URL}/api/security/groups/{NEW_GROUP.name}",
        json=NEW_GROUP.model_dump(),
        status=200,
    )

    responses.add(
        responses.POST,
        f"{URL}/api/security/groups/{NEW_GROUP.name}",
        json=NEW_GROUP.model_dump(),
        status=200,
    )
    artifactory_group = ArtifactoryGroup(AuthModel(url=URL, auth=AUTH))
    mocker.spy(artifactory_group, "get")
    artifactory_group.update(NEW_GROUP)

    artifactory_group.get.assert_called_with(NEW_GROUP.name)
    assert artifactory_group.get.call_count == 2


@responses.activate
def test_delete_group_fail_if_group_not_found(mocker):
    responses.add(responses.GET, f"{URL}/api/security/groups/{NEW_GROUP.name}", status=404)

    artifactory_group = ArtifactoryGroup(AuthModel(url=URL, auth=AUTH))
    mocker.spy(artifactory_group, "get")

    with pytest.raises(GroupNotFoundError):
        artifactory_group.delete(NEW_GROUP.name)

    artifactory_group.get.assert_called_once_with(NEW_GROUP.name)


@responses.activate
def test_delete_group_success(mocker):
    responses.add(
        responses.GET,
        f"{URL}/api/security/groups/{NEW_GROUP.name}",
        json=NEW_GROUP.model_dump(),
        status=200,
    )

    responses.add(responses.DELETE, f"{URL}/api/security/groups/{NEW_GROUP.name}", status=204)
    artifactory_group = ArtifactoryGroup(AuthModel(url=URL, auth=AUTH))
    mocker.spy(artifactory_group, "get")
    artifactory_group.delete(NEW_GROUP.name)

    artifactory_group.get.assert_called_once_with(NEW_GROUP.name)
