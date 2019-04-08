from unittest import mock

from pyartifactory import (
    ArtfictoryUser,
    ArtfictoryGroup,
    ArtfictorySecurity,
    ArtfictoryRepository,
)
from pyartifactory.models.Auth import AuthModel
from pyartifactory.models.Group import Group
from pyartifactory.models.Repository import LocalRepository, VirtualRepository
from pyartifactory.models.User import NewUser


URL = "http://host:port/artifactory"
AUTH = ("user", "password_or_apiKey")
USER = NewUser(name="test_user", password="test_password", email="test.test@test.com")
NEW_GROUP = Group(name="test_group", description="test_group")
LOCAL_REPO = LocalRepository(key="test_local_repo")
VIRTUAL_REPO = VirtualRepository(key="test_virtual_repo", rclass="virtual")
REMOTE_REPO = VirtualRepository(
    key="test_remote_repo", rclass="remote", url="http://host:port/some-repo"
)


class TestUser:
    def test_create_user(self):
        users_object_mock = mock.create_autospec(
            ArtfictoryUser(AuthModel(url=URL, auth=AUTH))
        )
        users_object_mock.create(USER)
        users_object_mock.create.assert_called_once_with(USER)

    def test_get_user(self):
        users_object_mock = mock.create_autospec(
            ArtfictoryUser(AuthModel(url=URL, auth=AUTH))
        )
        users_object_mock.get("user")
        users_object_mock.get.assert_called_once_with("user")

    def test_list_users(self):
        users_object_mock = mock.create_autospec(
            ArtfictoryUser(AuthModel(url=URL, auth=AUTH))
        )
        users_object_mock.list()
        users_object_mock.list.assert_called_once()

    def test_update_user(self):
        users_object_mock = mock.create_autospec(
            ArtfictoryUser(AuthModel(url=URL, auth=AUTH))
        )
        users_object_mock.update(USER)
        users_object_mock.update.assert_called_once_with(USER)

    def test_delete_user(self):
        users_object_mock = mock.create_autospec(
            ArtfictoryUser(AuthModel(url=URL, auth=AUTH))
        )
        users_object_mock.delete("user")
        users_object_mock.delete.assert_called_once_with("user")


class TestSecurity:
    def test_get_encrypted_password(self):
        security_object_mock = mock.create_autospec(
            ArtfictorySecurity(AuthModel(url=URL, auth=AUTH)), instance=True
        )
        security_object_mock.get_encrypted_password()
        security_object_mock.get_encrypted_password.assert_called_once()

    def test_create_api_key(self):
        security_object_mock = mock.create_autospec(
            ArtfictorySecurity(AuthModel(url=URL, auth=AUTH)), instance=True
        )
        security_object_mock.create_api_key()
        security_object_mock.create_api_key.assert_called_once()

    def test_regenerate_api_key(self):
        security_object_mock = mock.create_autospec(
            ArtfictorySecurity(AuthModel(url=URL, auth=AUTH)), instance=True
        )
        security_object_mock.regenerate_api_key()
        security_object_mock.regenerate_api_key.assert_called_once()

    def test_get_api_key(self):
        security_object_mock = mock.create_autospec(
            ArtfictorySecurity(AuthModel(url=URL, auth=AUTH)), instance=True
        )
        security_object_mock.get_api_key()
        security_object_mock.get_api_key.assert_called_once()

    def test_revoke_api_key(self):
        security_object_mock = mock.create_autospec(
            ArtfictorySecurity(AuthModel(url=URL, auth=AUTH)), instance=True
        )
        security_object_mock.revoke_api_key()
        security_object_mock.revoke_api_key.assert_called_once()

    def test_revoke_user_api_key(self):
        security_object_mock = mock.create_autospec(
            ArtfictorySecurity(AuthModel(url=URL, auth=AUTH)), instance=True
        )
        security_object_mock.revoke_user_api_key("user")
        security_object_mock.revoke_user_api_key.assert_called_once_with("user")


class TestGroup:
    def test_create_group(self):
        groups_object_mock = mock.create_autospec(
            ArtfictoryGroup(AuthModel(url=URL, auth=AUTH))
        )
        groups_object_mock.create(NEW_GROUP)
        groups_object_mock.create.assert_called_once_with(NEW_GROUP)

    def test_get_group(self):
        groups_object_mock = mock.create_autospec(
            ArtfictoryGroup(AuthModel(url=URL, auth=AUTH))
        )
        groups_object_mock.get("test_group")
        groups_object_mock.get.assert_called_once_with("test_group")

    def test_list_groups(self):
        groups_object_mock = mock.create_autospec(
            ArtfictoryGroup(AuthModel(url=URL, auth=AUTH))
        )
        groups_object_mock.list()
        groups_object_mock.list.assert_called_once()

    def test_update_group(self):
        groups_object_mock = mock.create_autospec(
            ArtfictoryGroup(AuthModel(url=URL, auth=AUTH))
        )
        groups_object_mock.update(NEW_GROUP)
        groups_object_mock.update.assert_called_once_with(NEW_GROUP)

    def test_delete_group(self):
        groups_object_mock = mock.create_autospec(
            ArtfictoryGroup(AuthModel(url=URL, auth=AUTH))
        )
        groups_object_mock.delete("test_group")
        groups_object_mock.delete.assert_called_once_with("test_group")


class TestLocalRepository:
    def test_create_local_repo(self):
        local_repo_mock = mock.create_autospec(
            ArtfictoryRepository(AuthModel(url=URL, auth=AUTH))
        )
        local_repo_mock.create_local_repo(LOCAL_REPO)
        local_repo_mock.create_local_repo.assert_called_once_with(LOCAL_REPO)

    def test_get_local_repo(self):
        local_repo_mock = mock.create_autospec(
            ArtfictoryRepository(AuthModel(url=URL, auth=AUTH))
        )
        local_repo_mock.get_local_repo(LOCAL_REPO.key)
        local_repo_mock.get_local_repo.assert_called_once_with(LOCAL_REPO.key)

    def test_update_local_repo(self):
        local_repo_mock = mock.create_autospec(
            ArtfictoryRepository(AuthModel(url=URL, auth=AUTH))
        )
        local_repo_mock.update_local_repo(LOCAL_REPO)
        local_repo_mock.update_local_repo.assert_called_once_with(LOCAL_REPO)


class TestVirtualRepository:
    def test_create_virtual_repo(self):
        virtual_repo_mock = mock.create_autospec(
            ArtfictoryRepository(AuthModel(url=URL, auth=AUTH))
        )
        virtual_repo_mock.create_virtual_repo(VIRTUAL_REPO)
        virtual_repo_mock.create_virtual_repo.assert_called_once_with(VIRTUAL_REPO)

    def test_get_virtual_repo(self):
        virtual_repo_mock = mock.create_autospec(
            ArtfictoryRepository(AuthModel(url=URL, auth=AUTH))
        )
        virtual_repo_mock.get_virtual_repo(VIRTUAL_REPO.key)
        virtual_repo_mock.get_virtual_repo.assert_called_once_with(VIRTUAL_REPO.key)

    def test_update_virtual_repo(self):
        virtual_repo_mock = mock.create_autospec(
            ArtfictoryRepository(AuthModel(url=URL, auth=AUTH))
        )
        virtual_repo_mock.update_virtual_repo(VIRTUAL_REPO)
        virtual_repo_mock.update_virtual_repo.assert_called_once_with(VIRTUAL_REPO)


class TestRemoteRepository:
    def test_create_remote_repo(self):
        local_repo_mock = mock.create_autospec(
            ArtfictoryRepository(AuthModel(url=URL, auth=AUTH))
        )
        local_repo_mock.create_virtual_repo(REMOTE_REPO)
        local_repo_mock.create_virtual_repo.assert_called_once_with(REMOTE_REPO)

    def test_get_remote_repo(self):
        local_repo_mock = mock.create_autospec(
            ArtfictoryRepository(AuthModel(url=URL, auth=AUTH))
        )
        local_repo_mock.get_virtual_repo(REMOTE_REPO.key)
        local_repo_mock.get_virtual_repo.assert_called_once_with(REMOTE_REPO.key)

    def test_update_remote_repo(self):
        local_repo_mock = mock.create_autospec(
            ArtfictoryRepository(AuthModel(url=URL, auth=AUTH))
        )
        local_repo_mock.update_virtual_repo(REMOTE_REPO)
        local_repo_mock.update_virtual_repo.assert_called_once_with(REMOTE_REPO)
