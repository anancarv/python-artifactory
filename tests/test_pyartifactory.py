import pytest
import responses

from pyartifactory import ArtfictoryUser, ArtfictoryGroup, ArtfictorySecurity
from pyartifactory.exception import (
    UserAlreadyExistsException,
    UserNotFoundException,
    GroupNotFoundException,
    GroupAlreadyExistsException,
)
from pyartifactory.models.Auth import AuthModel, PasswordModel, ApiKeyModel
from pyartifactory.models.Group import Group
from pyartifactory.models.Repository import LocalRepository, VirtualRepository
from pyartifactory.models.User import NewUser, UserResponse, SimpleUser

URL = "http://localhost:8080/artifactory"
AUTH = ("user", "password_or_apiKey")
SIMPLE_USER = SimpleUser(name="test_user")
USER = UserResponse(name="test_user", email="test.test@test.com")
NEW_USER = NewUser(
    name="test_user", password="test_password", email="test.test@test.com"
)
NEW_GROUP = Group(name="test_group", description="test_group")
PASSWORD = PasswordModel(password="test_password")
API_KEY = ApiKeyModel(apiKey="test_api_key")
LOCAL_REPO = LocalRepository(key="test_local_repo")
VIRTUAL_REPO = VirtualRepository(key="test_virtual_repo", rclass="virtual")
REMOTE_REPO = VirtualRepository(
    key="test_remote_repo", rclass="remote", url="http://host:port/some-repo"
)


class TestUser:
    @responses.activate
    def test_create_user_fail_if_user_already_exists(self, mocker):
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

    @responses.activate
    def test_create_user_success(self, mocker):
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

    @responses.activate
    def test_get_user_error_not_found(self):
        responses.add(
            responses.GET, f"{URL}/api/security/users/{USER.name}", status=404
        )

        artifactory_user = ArtfictoryUser(AuthModel(url=URL, auth=AUTH))
        with pytest.raises(UserNotFoundException):
            artifactory_user.get(NEW_USER.name)

    @responses.activate
    def test_get_user_success(self, mocker):
        responses.add(
            responses.GET,
            f"{URL}/api/security/users/{USER.name}",
            json=USER.dict(),
            status=200,
        )

        artifactory_user = ArtfictoryUser(AuthModel(url=URL, auth=AUTH))
        mocker.spy(artifactory_user, "get")
        artifactory_user.get(NEW_USER.name)

        artifactory_user.get.assert_called_with(NEW_USER.name)

    @responses.activate
    def test_list_user_success(self, mocker):
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

    @responses.activate
    def test_update_user_fail_if_user_not_found(self, mocker):
        responses.add(
            responses.GET, f"{URL}/api/security/users/{NEW_USER.name}", status=404
        )

        artifactory_user = ArtfictoryUser(AuthModel(url=URL, auth=AUTH))
        mocker.spy(artifactory_user, "get")
        with pytest.raises(UserNotFoundException):
            artifactory_user.update(NEW_USER)

        artifactory_user.get.assert_called_once_with(NEW_USER.name)

    @responses.activate
    def test_update_user_success(self, mocker):
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

    @responses.activate
    def test_delete_user_fail_if_user_not_found(self, mocker):
        responses.add(
            responses.GET, f"{URL}/api/security/users/{NEW_USER.name}", status=404
        )

        artifactory_user = ArtfictoryUser(AuthModel(url=URL, auth=AUTH))
        mocker.spy(artifactory_user, "get")

        with pytest.raises(UserNotFoundException):
            artifactory_user.delete(NEW_USER.name)

        artifactory_user.get.assert_called_once_with(NEW_USER.name)

    @responses.activate
    def test_delete_user_success(self, mocker):
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


class TestGroup:
    @responses.activate
    def test_create_group_fail_if_group_already_exists(self, mocker):
        responses.add(
            responses.GET,
            f"{URL}/api/security/groups/{NEW_GROUP.name}",
            json=NEW_GROUP.dict(),
            status=200,
        )

        artifactory_group = ArtfictoryGroup(AuthModel(url=URL, auth=AUTH))
        mocker.spy(artifactory_group, "get")
        with pytest.raises(GroupAlreadyExistsException):
            artifactory_group.create(NEW_GROUP)

        artifactory_group.get.assert_called_once_with(NEW_GROUP.name)

    @responses.activate
    def test_create_group_success(self, mocker):
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

        artifactory_group = ArtfictoryGroup(AuthModel(url=URL, auth=AUTH))
        mocker.spy(artifactory_group, "get")
        with pytest.raises(GroupNotFoundException):
            artifactory_group.create(NEW_GROUP)

        artifactory_group.get.assert_called_with(NEW_GROUP.name)
        assert artifactory_group.get.call_count == 2

    @responses.activate
    def test_get_group_error_not_found(self):
        responses.add(
            responses.GET, f"{URL}/api/security/groups/{NEW_GROUP.name}", status=404
        )

        artifactory_group = ArtfictoryGroup(AuthModel(url=URL, auth=AUTH))
        with pytest.raises(GroupNotFoundException):
            artifactory_group.get(NEW_GROUP.name)

    @responses.activate
    def test_get_group_success(self, mocker):
        responses.add(
            responses.GET,
            f"{URL}/api/security/groups/{NEW_GROUP.name}",
            json=NEW_GROUP.dict(),
            status=200,
        )

        artifactory_group = ArtfictoryGroup(AuthModel(url=URL, auth=AUTH))
        mocker.spy(artifactory_group, "get")
        artifactory_group.get(NEW_GROUP.name)

        artifactory_group.get.assert_called_with(NEW_GROUP.name)

    @responses.activate
    def test_list_group_success(self, mocker):
        responses.add(
            responses.GET,
            f"{URL}/api/security/groups",
            json=[NEW_GROUP.dict()],
            status=200,
        )

        artifactory_group = ArtfictoryGroup(AuthModel(url=URL, auth=AUTH))
        mocker.spy(artifactory_group, "list")
        artifactory_group.list()

        artifactory_group.list.assert_called_once()

    @responses.activate
    def test_update_group_fail_if_group_not_found(self, mocker):
        responses.add(
            responses.GET, f"{URL}/api/security/groups/{NEW_GROUP.name}", status=404
        )

        artifactory_group = ArtfictoryGroup(AuthModel(url=URL, auth=AUTH))
        mocker.spy(artifactory_group, "get")
        with pytest.raises(GroupNotFoundException):
            artifactory_group.update(NEW_GROUP)

        artifactory_group.get.assert_called_once_with(NEW_GROUP.name)

    @responses.activate
    def test_update_group_success(self, mocker):
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
        artifactory_group = ArtfictoryGroup(AuthModel(url=URL, auth=AUTH))
        mocker.spy(artifactory_group, "get")
        artifactory_group.update(NEW_GROUP)

        artifactory_group.get.assert_called_with(NEW_GROUP.name)
        assert artifactory_group.get.call_count == 2

    @responses.activate
    def test_delete_group_fail_if_group_not_found(self, mocker):
        responses.add(
            responses.GET, f"{URL}/api/security/groups/{NEW_GROUP.name}", status=404
        )

        artifactory_group = ArtfictoryGroup(AuthModel(url=URL, auth=AUTH))
        mocker.spy(artifactory_group, "get")

        with pytest.raises(GroupNotFoundException):
            artifactory_group.delete(NEW_GROUP.name)

        artifactory_group.get.assert_called_once_with(NEW_GROUP.name)

    @responses.activate
    def test_delete_group_success(self, mocker):
        responses.add(
            responses.GET,
            f"{URL}/api/security/groups/{NEW_GROUP.name}",
            json=NEW_GROUP.dict(),
            status=200,
        )

        responses.add(
            responses.DELETE, f"{URL}/api/security/groups/{NEW_GROUP.name}", status=204
        )
        artifactory_group = ArtfictoryGroup(AuthModel(url=URL, auth=AUTH))
        mocker.spy(artifactory_group, "get")
        artifactory_group.delete(NEW_GROUP.name)

        artifactory_group.get.assert_called_once_with(NEW_GROUP.name)


class TestSecurity:
    @responses.activate
    def test_get_encrypted_password(self):
        data = PASSWORD.dict()
        data["password"] = PASSWORD.password.get_secret_value()
        responses.add(
            responses.GET,
            f"{URL}/api/security/encryptedPassword",
            json=data,
            status=200,
        )

        artifactory_security = ArtfictorySecurity(AuthModel(url=URL, auth=AUTH))
        artifactory_security.get_encrypted_password()

    @responses.activate
    def test_create_api_key(self):
        data = API_KEY.dict()
        data["apiKey"] = API_KEY.apiKey.get_secret_value()
        responses.add(
            responses.POST, f"{URL}/api/security/apiKey", json=data, status=200
        )

        artifactory_security = ArtfictorySecurity(AuthModel(url=URL, auth=AUTH))
        artifactory_security.create_api_key()

    @responses.activate
    def test_regenerate_api_key(self):
        data = API_KEY.dict()
        data["apiKey"] = API_KEY.apiKey.get_secret_value()
        responses.add(
            responses.PUT, f"{URL}/api/security/apiKey", json=data, status=200
        )

        artifactory_security = ArtfictorySecurity(AuthModel(url=URL, auth=AUTH))
        artifactory_security.regenerate_api_key()

    @responses.activate
    def test_get_api_key(self):
        data = API_KEY.dict()
        data["apiKey"] = API_KEY.apiKey.get_secret_value()
        responses.add(
            responses.GET, f"{URL}/api/security/apiKey", json=data, status=200
        )

        artifactory_security = ArtfictorySecurity(AuthModel(url=URL, auth=AUTH))
        artifactory_security.get_api_key()

    @responses.activate
    def test_revoke_api_key(self):
        responses.add(responses.DELETE, f"{URL}/api/security/apiKey", status=200)

        artifactory_security = ArtfictorySecurity(AuthModel(url=URL, auth=AUTH))
        artifactory_security.revoke_api_key()

    @responses.activate
    def test_revoke_user_api_key(self):
        responses.add(
            responses.DELETE, f"{URL}/api/security/apiKey/{USER.name}", status=200
        )

        artifactory_security = ArtfictorySecurity(AuthModel(url=URL, auth=AUTH))
        artifactory_security.revoke_user_api_key(USER.name)
