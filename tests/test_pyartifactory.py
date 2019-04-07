import mock
import pytest

from pyartifactory import ArtfictoryUser, ArtfictoryGroup, ArtfictorySecurity
from pyartifactory.models.Auth import AuthModel
from pyartifactory.models.Group import Group
from pyartifactory.models.User import NewUser


pytest.url = "http://host:port/artifactory"
pytest.auth = ("user", "password_or_apiKey")
pytest.user = NewUser(
    name="test_user", password="test_password", email="test.test@test.com"
)
pytest.new_group = Group(name="test_group", description="test_group")


class TestUser:
    def test_create_user(self):
        users_object_mock = mock.create_autospec(
            ArtfictoryUser(AuthModel(url=pytest.url, auth=pytest.auth))
        )
        users_object_mock.create(pytest.user)
        users_object_mock.create.assert_called_once_with(pytest.user)

    def test_get_user(self):
        users_object_mock = mock.create_autospec(
            ArtfictoryUser(AuthModel(url=pytest.url, auth=pytest.auth))
        )
        users_object_mock.get("user")
        users_object_mock.get.assert_called_once_with("user")

    def test_list_users(self):
        users_object_mock = mock.create_autospec(
            ArtfictoryUser(AuthModel(url=pytest.url, auth=pytest.auth))
        )
        users_object_mock.list()
        users_object_mock.list.assert_called_once()

    def test_update_user(self):
        users_object_mock = mock.create_autospec(
            ArtfictoryUser(AuthModel(url=pytest.url, auth=pytest.auth))
        )
        users_object_mock.update(pytest.user)
        users_object_mock.update.assert_called_once_with(pytest.user)

    def test_delete_user(self):
        users_object_mock = mock.create_autospec(
            ArtfictoryUser(AuthModel(url=pytest.url, auth=pytest.auth))
        )
        users_object_mock.delete("user")
        users_object_mock.delete.assert_called_once_with("user")


class TestSecurity:
    def test_get_encrypted_password(self):
        security_object_mock = mock.create_autospec(
            ArtfictorySecurity(AuthModel(url=pytest.url, auth=pytest.auth)),
            instance=True,
        )
        security_object_mock.get_encrypted_password()
        security_object_mock.get_encrypted_password.assert_called_once()

    def test_create_api_key(self):
        security_object_mock = mock.create_autospec(
            ArtfictorySecurity(AuthModel(url=pytest.url, auth=pytest.auth)),
            instance=True,
        )
        security_object_mock.create_api_key()
        security_object_mock.create_api_key.assert_called_once()

    def test_regenerate_api_key(self):
        security_object_mock = mock.create_autospec(
            ArtfictorySecurity(AuthModel(url=pytest.url, auth=pytest.auth)),
            instance=True,
        )
        security_object_mock.regenerate_api_key()
        security_object_mock.regenerate_api_key.assert_called_once()

    def test_get_api_key(self):
        security_object_mock = mock.create_autospec(
            ArtfictorySecurity(AuthModel(url=pytest.url, auth=pytest.auth)),
            instance=True,
        )
        security_object_mock.get_api_key()
        security_object_mock.get_api_key.assert_called_once()

    def test_revoke_api_key(self):
        security_object_mock = mock.create_autospec(
            ArtfictorySecurity(AuthModel(url=pytest.url, auth=pytest.auth)),
            instance=True,
        )
        security_object_mock.revoke_api_key()
        security_object_mock.revoke_api_key.assert_called_once()

    def test_revoke_user_api_key(self):
        security_object_mock = mock.create_autospec(
            ArtfictorySecurity(AuthModel(url=pytest.url, auth=pytest.auth)),
            instance=True,
        )
        security_object_mock.revoke_user_api_key("user")
        security_object_mock.revoke_user_api_key.assert_called_once_with("user")


class TestGroup:
    def test_create_group(self):
        groups_object_mock = mock.create_autospec(
            ArtfictoryGroup(AuthModel(url=pytest.url, auth=pytest.auth))
        )
        groups_object_mock.create(pytest.new_group)
        groups_object_mock.create.assert_called_once_with(pytest.new_group)

    def test_get_group(self):
        groups_object_mock = mock.create_autospec(
            ArtfictoryGroup(AuthModel(url=pytest.url, auth=pytest.auth))
        )
        groups_object_mock.get("test_group")
        groups_object_mock.get.assert_called_once_with("test_group")

    def test_list_groups(self):
        groups_object_mock = mock.create_autospec(
            ArtfictoryGroup(AuthModel(url=pytest.url, auth=pytest.auth))
        )
        groups_object_mock.list()
        groups_object_mock.list.assert_called_once()

    def test_update_group(self):
        groups_object_mock = mock.create_autospec(
            ArtfictoryGroup(AuthModel(url=pytest.url, auth=pytest.auth))
        )
        groups_object_mock.update(pytest.new_group)
        groups_object_mock.update.assert_called_once_with(pytest.new_group)

    def test_delete_group(self):
        groups_object_mock = mock.create_autospec(
            ArtfictoryGroup(AuthModel(url=pytest.url, auth=pytest.auth))
        )
        groups_object_mock.delete("test_group")
        groups_object_mock.delete.assert_called_once_with("test_group")
