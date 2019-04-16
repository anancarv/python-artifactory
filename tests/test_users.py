import pytest
import responses

from pyartifactory import ArtfictoryUser
from pyartifactory.exception import UserAlreadyExistsException, UserNotFoundException
from pyartifactory.models import AuthModel, NewUser, UserResponse, SimpleUser

URL = "http://localhost:8080/artifactory"
AUTH = ("user", "password_or_apiKey")
SIMPLE_USER = SimpleUser(name="test_user", uri="https:some.uri")
USER = UserResponse(name="test_user", email="test.test@test.com")
NEW_USER = NewUser(name="test_user", password="test", email="test.test@test.com")


class TestUser:
    @staticmethod
    @responses.activate
    def test_create_user_fail_if_user_already_exists(mocker):
        responses.add(
            responses.GET,
            f"{URL}/api/security/users/{USER.name}",
            json=USER.dict(),
            status=200,
        )

        artifactory_user = ArtfictoryUser(AuthModel(url=URL, auth=AUTH))
        mocker.spy(artifactory_user, "get")
        with pytest.raises(UserAlreadyExistsException):
            artifactory_user.create(NEW_USER)

        artifactory_user.get.assert_called_once_with(NEW_USER.name)

    @staticmethod
    @responses.activate
    def test_create_user_success(mocker):
        responses.add(
            responses.GET,
            f"{URL}/api/security/users/{USER.name}",
            json=USER.dict(),
            status=404,
        )
        responses.add(
            responses.PUT,
            f"{URL}/api/security/users/{USER.name}",
            json=USER.dict(),
            status=201,
        )

        artifactory_user = ArtfictoryUser(AuthModel(url=URL, auth=AUTH))
        mocker.spy(artifactory_user, "get")
        with pytest.raises(UserNotFoundException):
            artifactory_user.create(NEW_USER)

        artifactory_user.get.assert_called_with(NEW_USER.name)
        assert artifactory_user.get.call_count == 2

    @staticmethod
    @responses.activate
    def test_get_user_error_not_found():
        responses.add(
            responses.GET, f"{URL}/api/security/users/{USER.name}", status=404
        )

        artifactory_user = ArtfictoryUser(AuthModel(url=URL, auth=AUTH))
        with pytest.raises(UserNotFoundException):
            artifactory_user.get(NEW_USER.name)

    @staticmethod
    @responses.activate
    def test_get_user_success(mocker):
        responses.add(
            responses.GET,
            f"{URL}/api/security/users/{USER.name}",
            json=USER.dict(),
            status=200,
        )

        artifactory_user = ArtfictoryUser(AuthModel(url=URL, auth=AUTH))
        mocker.spy(artifactory_user, "get")
        artifactory_user.get(NEW_USER.name)

        artifactory_user.get.assert_called_once()

    @staticmethod
    @responses.activate
    def test_list_user_success(mocker):
        responses.add(
            responses.GET,
            f"{URL}/api/security/users",
            json=[SIMPLE_USER.dict()],
            status=200,
        )

        artifactory_user = ArtfictoryUser(AuthModel(url=URL, auth=AUTH))
        mocker.spy(artifactory_user, "list")
        artifactory_user.list()

        artifactory_user.list.assert_called_once()

    @staticmethod
    @responses.activate
    def test_update_user_fail_if_user_not_found(mocker):
        responses.add(
            responses.GET, f"{URL}/api/security/users/{NEW_USER.name}", status=404
        )

        artifactory_user = ArtfictoryUser(AuthModel(url=URL, auth=AUTH))
        mocker.spy(artifactory_user, "get")
        with pytest.raises(UserNotFoundException):
            artifactory_user.update(NEW_USER)

        artifactory_user.get.assert_called_once_with(NEW_USER.name)

    @staticmethod
    @responses.activate
    def test_update_user_success(mocker):
        responses.add(
            responses.GET,
            f"{URL}/api/security/users/{NEW_USER.name}",
            json=USER.dict(),
            status=200,
        )

        responses.add(
            responses.POST,
            f"{URL}/api/security/users/{NEW_USER.name}",
            json=USER.dict(),
            status=200,
        )
        artifactory_user = ArtfictoryUser(AuthModel(url=URL, auth=AUTH))
        mocker.spy(artifactory_user, "get")
        artifactory_user.update(NEW_USER)

        artifactory_user.get.assert_called_with(NEW_USER.name)
        assert artifactory_user.get.call_count == 2

    @staticmethod
    @responses.activate
    def test_delete_user_fail_if_user_not_found(mocker):
        responses.add(
            responses.GET, f"{URL}/api/security/users/{NEW_USER.name}", status=404
        )

        artifactory_user = ArtfictoryUser(AuthModel(url=URL, auth=AUTH))
        mocker.spy(artifactory_user, "get")

        with pytest.raises(UserNotFoundException):
            artifactory_user.delete(NEW_USER.name)

        artifactory_user.get.assert_called_once_with(NEW_USER.name)

    @staticmethod
    @responses.activate
    def test_delete_user_success(mocker):
        responses.add(
            responses.GET,
            f"{URL}/api/security/users/{NEW_USER.name}",
            json=USER.dict(),
            status=200,
        )

        responses.add(
            responses.DELETE, f"{URL}/api/security/users/{NEW_USER.name}", status=204
        )
        artifactory_user = ArtfictoryUser(AuthModel(url=URL, auth=AUTH))
        mocker.spy(artifactory_user, "get")
        artifactory_user.delete(NEW_USER.name)

        artifactory_user.get.assert_called_once_with(NEW_USER.name)
