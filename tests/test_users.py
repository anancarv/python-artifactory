from __future__ import annotations

import json

import pytest
import responses

from pyartifactory import ArtifactoryUser
from pyartifactory.exception import UserAlreadyExistsError, UserNotFoundError
from pyartifactory.models import AuthModel, NewUser, SimpleUser, User, UserResponse

URL = "http://localhost:8080/artifactory"
AUTH = ("user", "password_or_apiKey")
SIMPLE_USER = SimpleUser(name="test_user", uri="https://some.uri", status="enabled")
USER = UserResponse(name="test_user", email="test.test@test.com")
USER_TO_UPDATE = User(name="test_user", email="test.test2@test.com")
NEW_USER = NewUser(name="test_user", password="test", email="test.test@test.com")


@responses.activate
def test_create_user_fail_if_user_already_exists(mocker):
    responses.add(
        responses.GET,
        f"{URL}/api/security/users/{USER.name}",
        json=USER.model_dump(),
        status=200,
    )

    artifactory_user = ArtifactoryUser(AuthModel(url=URL, auth=AUTH))
    mocker.spy(artifactory_user, "get")
    with pytest.raises(UserAlreadyExistsError):
        artifactory_user.create(NEW_USER)

    artifactory_user.get.assert_called_once_with(NEW_USER.name)


@responses.activate
def test_create_user_success(mocker):
    responses.add(responses.GET, f"{URL}/api/security/users/{USER.name}", status=404)
    responses.add(
        responses.PUT,
        f"{URL}/api/security/users/{USER.name}",
        json=USER.model_dump(),
        status=201,
    )
    responses.add(
        responses.GET,
        f"{URL}/api/security/users/{USER.name}",
        json=USER.model_dump(),
        status=200,
    )

    artifactory_user = ArtifactoryUser(AuthModel(url=URL, auth=AUTH))
    mocker.spy(artifactory_user, "get")
    user = artifactory_user.create(NEW_USER)

    artifactory_user.get.assert_called_with(NEW_USER.name)
    assert artifactory_user.get.call_count == 2
    assert user.model_dump() == USER.model_dump()


@responses.activate
def test_get_user_error_not_found():
    responses.add(responses.GET, f"{URL}/api/security/users/{USER.name}", status=404)

    artifactory_user = ArtifactoryUser(AuthModel(url=URL, auth=AUTH))
    with pytest.raises(UserNotFoundError):
        artifactory_user.get(NEW_USER.name)


@responses.activate
def test_get_user_success(mocker):
    responses.add(
        responses.GET,
        f"{URL}/api/security/users/{USER.name}",
        json=USER.model_dump(),
        status=200,
    )

    artifactory_user = ArtifactoryUser(AuthModel(url=URL, auth=AUTH))
    mocker.spy(artifactory_user, "get")
    artifactory_user.get(NEW_USER.name)

    artifactory_user.get.assert_called_once()


# Disable because mock can't serialize pydantic2 HttpUrl
@responses.activate
def test_list_user_success(mocker):
    responses.add(
        responses.GET,
        f"{URL}/api/security/users",
        json=[json.loads(SIMPLE_USER.model_dump_json())],
        status=200,
    )

    artifactory_user = ArtifactoryUser(AuthModel(url=URL, auth=AUTH))
    mocker.spy(artifactory_user, "list")
    artifactory_user.list()

    artifactory_user.list.assert_called_once()


@responses.activate
def test_update_user_fail_if_user_not_found(mocker):
    responses.add(responses.GET, f"{URL}/api/security/users/{USER_TO_UPDATE.name}", status=404)

    artifactory_user = ArtifactoryUser(AuthModel(url=URL, auth=AUTH))
    mocker.spy(artifactory_user, "get")
    with pytest.raises(UserNotFoundError):
        artifactory_user.update(USER_TO_UPDATE)

    artifactory_user.get.assert_called_once_with(NEW_USER.name)


@responses.activate
def test_update_user_success(mocker):
    responses.add(
        responses.GET,
        f"{URL}/api/security/users/{USER_TO_UPDATE.name}",
        json=USER.model_dump(),
        status=200,
    )

    responses.add(
        responses.POST,
        f"{URL}/api/security/users/{USER_TO_UPDATE.name}",
        json=USER.model_dump(),
        status=200,
    )
    artifactory_user = ArtifactoryUser(AuthModel(url=URL, auth=AUTH))
    mocker.spy(artifactory_user, "get")
    artifactory_user.update(USER_TO_UPDATE)

    artifactory_user.get.assert_called_with(NEW_USER.name)
    assert artifactory_user.get.call_count == 2


@responses.activate
def test_delete_user_fail_if_user_not_found(mocker):
    responses.add(responses.GET, f"{URL}/api/security/users/{NEW_USER.name}", status=404)

    artifactory_user = ArtifactoryUser(AuthModel(url=URL, auth=AUTH))
    mocker.spy(artifactory_user, "get")

    with pytest.raises(UserNotFoundError):
        artifactory_user.delete(NEW_USER.name)

    artifactory_user.get.assert_called_once_with(NEW_USER.name)


@responses.activate
def test_delete_user_success(mocker):
    responses.add(
        responses.GET,
        f"{URL}/api/security/users/{NEW_USER.name}",
        json=USER.model_dump(),
        status=200,
    )

    responses.add(responses.DELETE, f"{URL}/api/security/users/{NEW_USER.name}", status=204)
    artifactory_user = ArtifactoryUser(AuthModel(url=URL, auth=AUTH))
    mocker.spy(artifactory_user, "get")
    artifactory_user.delete(NEW_USER.name)

    artifactory_user.get.assert_called_once_with(NEW_USER.name)


@responses.activate
def test_unlock_user_success(mocker):
    responses.add(responses.POST, f"{URL}/api/security/unlockUsers/{NEW_USER.name}", status=200)
    artifactory_user = ArtifactoryUser(AuthModel(url=URL, auth=AUTH))
    artifactory_user.unlock(NEW_USER.name)
