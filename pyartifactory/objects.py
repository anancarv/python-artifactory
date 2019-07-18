import logging
from typing import List

import requests

from pyartifactory.exception import (
    UserNotFoundException,
    UserAlreadyExistsException,
    GroupNotFoundException,
    RepositoryAlreadyExistsException,
    GroupAlreadyExistsException,
    RepositoryNotFoundException,
    PermissionAlreadyExistsException,
    PermissionNotFoundException,
)
from pyartifactory.models.Permission import Permission, SimplePermission
from pyartifactory.models.Auth import AuthModel, ApiKeyModel, PasswordModel
from pyartifactory.models.Group import Group
from pyartifactory.models.Repository import (
    LocalRepository,
    VirtualRepository,
    LocalRepositoryResponse,
    VirtualRepositoryResponse,
    RemoteRepository,
    RemoteRepositoryResponse,
    SimpleRepository,
)
from pyartifactory.models.User import UserResponse, NewUser, SimpleUser


class ArtifactoryAuth:
    def __init__(self, artifactory: AuthModel) -> None:
        self._artifactory = artifactory
        self._auth = (
            self._artifactory.auth[0],
            self._artifactory.auth[1].get_secret_value(),
        )
        self._verify = self._artifactory.verify
        self._cert = self._artifactory.cert


class ArtfictoryUser(ArtifactoryAuth):
    _uri = "security/users"

    def __init__(self, artifactory: AuthModel) -> None:
        super(ArtfictoryUser, self).__init__(artifactory)

    def create(self, user: NewUser) -> UserResponse:
        """
        Create user
        :param user: NewUser object
        :return: User
        """
        username = user.name
        try:
            self.get(username)
            logging.debug(f"User {username} already exists")
            raise UserAlreadyExistsException(f"User {username} already exists")
        except UserNotFoundException:
            request_url = f"{self._artifactory.url}/api/{self._uri}/{username}"
            data = user.dict()
            data["password"] = user.password.get_secret_value()
            r = requests.put(
                request_url,
                json=data,
                auth=self._auth,
                verify=self._verify,
                cert=self._cert,
            )
            r.raise_for_status()
            return self.get(user.name)

    def get(self, name: str) -> UserResponse:
        """
        Read user from artifactory. Fill object if exist
        :param name: Name of the user to retrieve
        :return: UserModel
        """
        request_url = f"{self._artifactory.url}/api/{self._uri}/{name}"
        r = requests.get(
            request_url, auth=self._auth, verify=self._verify, cert=self._cert
        )
        if r.status_code == 404 or r.status_code == 400:
            logging.debug(f"User {name} does not exist")
            raise UserNotFoundException(f"{name} does not exist")
        else:
            logging.debug(f"User {name} exists")
            r.raise_for_status()
            return UserResponse(**r.json())

    def list(self) -> List[SimpleUser]:
        """
        Lists all the users
        :return: UserList
        """
        request_url = f"{self._artifactory.url}/api/{self._uri}"
        r = requests.get(
            request_url, auth=self._auth, verify=self._verify, cert=self._cert
        )
        r.raise_for_status()
        user_list = []
        for user in r.json():
            user_list.append(SimpleUser(**user))
        return user_list

    def update(self, user: NewUser) -> UserResponse:
        """
        Updates an artifactory user
        :param user: NewUser object
        :return: UserModel
        """
        username = user.name
        try:
            self.get(username)
            request_url = f"{self._artifactory.url}/api/{self._uri}/{username}"
            data = user.dict()
            data["password"] = user.password.get_secret_value()
            r = requests.post(
                request_url,
                json=data,
                auth=self._auth,
                verify=self._verify,
                cert=self._cert,
            )
            r.raise_for_status()
            return self.get(username)
        except UserNotFoundException:
            raise

    def delete(self, name: str) -> None:
        """
        Remove user
        :param name: Name of the user to delete
        :return: None
        """
        try:
            self.get(name)
            request_url = f"{self._artifactory.url}/api/{self._uri}/{name}"
            r = requests.delete(
                request_url, auth=self._auth, verify=self._verify, cert=self._cert
            )
            r.raise_for_status()
        except UserNotFoundException:
            raise


class ArtfictorySecurity(ArtifactoryAuth):
    _uri = "security"

    def __init__(self, artifactory: AuthModel) -> None:
        super(ArtfictorySecurity, self).__init__(artifactory)

    def get_encrypted_password(self) -> PasswordModel:
        """
        Get the encrypted password of the authenticated requestor.
        :return: str
        """
        request_url = f"{self._artifactory.url}/api/{self._uri}/encryptedPassword"
        r = requests.get(
            request_url, auth=self._auth, verify=self._verify, cert=self._cert
        )
        r.raise_for_status()
        return PasswordModel(**r.json())

    def create_api_key(self) -> ApiKeyModel:
        """
        Create an API key for the current user.
        :return: Error if API key already exists - use regenerate API key instead.
        """
        request_url = f"{self._artifactory.url}/api/{self._uri}/apiKey"
        r = requests.post(
            request_url, auth=self._auth, verify=self._verify, cert=self._cert
        )
        r.raise_for_status()
        return ApiKeyModel(**r.json())

    def regenerate_api_key(self) -> ApiKeyModel:
        """
        Regenerate an API key for the current user
        :return: API key
        """
        request_url = f"{self._artifactory.url}/api/{self._uri}/apiKey"
        r = requests.put(
            request_url, auth=self._auth, verify=self._verify, cert=self._cert
        )
        r.raise_for_status()
        return ApiKeyModel(**r.json())

    def get_api_key(self) -> ApiKeyModel:
        """
        Get the current user's own API key
        :return: API key
        """
        request_url = f"{self._artifactory.url}/api/{self._uri}/apiKey"
        r = requests.get(
            request_url, auth=self._auth, verify=self._verify, cert=self._cert
        )
        r.raise_for_status()
        return ApiKeyModel(**r.json())

    def revoke_api_key(self) -> None:
        """
        Revokes the current user's API key
        :return: None
        """
        request_url = f"{self._artifactory.url}/api/{self._uri}/apiKey"
        r = requests.delete(
            request_url, auth=self._auth, verify=self._verify, cert=self._cert
        )
        r.raise_for_status()

    def revoke_user_api_key(self, name: str) -> None:
        """
        Revokes the API key of another user
        :param name: name of the user to whom api key has to be revoked
        :return: None
        """
        request_url = f"{self._artifactory.url}/api/{self._uri}/apiKey/{name}"
        r = requests.delete(
            request_url, auth=self._auth, verify=self._verify, cert=self._cert
        )
        r.raise_for_status()


class ArtfictoryGroup(ArtifactoryAuth):
    _uri = "security/groups"

    def __init__(self, artifactory: AuthModel) -> None:
        super(ArtfictoryGroup, self).__init__(artifactory)

    def create(self, group: Group) -> Group:
        """
        Creates a new group in Artifactory or replaces an existing group
        :param group: Group to create
        :return: Created group
        """
        group_name = group.name
        try:
            self.get(group_name)
            logging.debug(f"Group {group_name} already exists")
            raise GroupAlreadyExistsException(f"Group {group_name} already exists")
        except GroupNotFoundException:
            request_url = f"{self._artifactory.url}/api/{self._uri}/{group_name}"
            r = requests.put(
                request_url,
                json=group.dict(),
                auth=self._auth,
                verify=self._verify,
                cert=self._cert,
            )
            r.raise_for_status()
            return self.get(group.name)

    def get(self, name: str) -> Group:
        """
        Get the details of an Artifactory Group
        :param name: Name of the group to retrieve
        :return: Found artifactory group
        """
        request_url = f"{self._artifactory.url}/api/{self._uri}/{name}"
        r = requests.get(
            request_url, auth=self._auth, verify=self._verify, cert=self._cert
        )
        if r.status_code == 404 or r.status_code == 400:
            logging.debug(f"Group {name} does not exist")
            raise GroupNotFoundException(f"Group {name} does not exist")
        else:
            logging.debug(f"Group {name} exists")
            r.raise_for_status()
            return Group(**r.json())

    def list(self) -> List[Group]:
        """
        Lists all the groups
        :return: GroupList
        """
        request_url = f"{self._artifactory.url}/api/{self._uri}"
        r = requests.get(
            request_url, auth=self._auth, verify=self._verify, cert=self._cert
        )
        r.raise_for_status()

        group_list = []
        for group in r.json():
            group_list.append(Group(**group))

        return group_list

    def update(self, group: Group) -> Group:
        """
        Updates an exiting group in Artifactory with the provided group details.
        :param group: Group to be updated
        :return: Updated group
        """
        group_name = group.name
        try:
            self.get(group_name)
            request_url = f"{self._artifactory.url}/api/{self._uri}/{group_name}"
            r = requests.post(
                request_url,
                json=group.dict(),
                auth=self._auth,
                verify=self._verify,
                cert=self._cert,
            )
            r.raise_for_status()
            return self.get(group_name)
        except GroupNotFoundException:
            raise

    def delete(self, name: str) -> None:
        """
        Removes a group
        :param name: Name of the group to delete
        :return: None
        """
        try:
            self.get(name)
            request_url = f"{self._artifactory.url}/api/{self._uri}/{name}"
            r = requests.delete(
                request_url, auth=self._auth, verify=self._verify, cert=self._cert
            )
            r.raise_for_status()
        except GroupNotFoundException:
            raise


class ArtfictoryRepository(ArtifactoryAuth):
    _uri = "repositories"

    def __init__(self, artifactory: AuthModel) -> None:
        super(ArtfictoryRepository, self).__init__(artifactory)

    # Local repositories operations
    def create_local_repo(self, repo: LocalRepository) -> LocalRepositoryResponse:
        """
        Creates a new local repository
        :param repo: LocalRepository object
        :return: LocalRepositoryResponse object
        """
        repo_name = repo.key
        try:
            self.get_local_repo(repo_name)
            logging.debug(f"Repository {repo_name} already exists")
            raise RepositoryAlreadyExistsException(
                f"Repository {repo_name} already exists"
            )
        except RepositoryNotFoundException:
            request_url = f"{self._artifactory.url}/api/{self._uri}/{repo_name}"
            r = requests.put(
                request_url,
                json=repo.dict(),
                auth=self._auth,
                verify=self._verify,
                cert=self._cert,
            )
            r.raise_for_status()
            return self.get_local_repo(repo_name)

    def get_local_repo(self, repo_name: str) -> LocalRepositoryResponse:
        """
        Finds repository in artifactory. Fill object if exist
        :param repo_name: Name of the repository to retrieve
        :return: LocalRepositoryResponse object
        """
        request_url = f"{self._artifactory.url}/api/{self._uri}/{repo_name}"
        r = requests.get(
            request_url, auth=self._auth, verify=self._verify, cert=self._cert
        )
        if r.status_code == 404 or r.status_code == 400:
            logging.debug(f"Repository {repo_name} does not exist")
            raise RepositoryNotFoundException(f" Repository {repo_name} does not exist")
        else:
            logging.debug(f"Repository {repo_name} exists")
            r.raise_for_status()
            return LocalRepositoryResponse(**r.json())

    def update_local_repo(self, repo: LocalRepository) -> LocalRepositoryResponse:
        """
        Updates an artifactory repository
        :param repo: LocalRepository object
        :return: LocalRepositoryResponse
        """
        repo_name = repo.key
        try:
            self.get_local_repo(repo_name)
            request_url = f"{self._artifactory.url}/api/{self._uri}/{repo_name}"
            r = requests.post(
                request_url,
                json=repo.dict(),
                auth=self._auth,
                verify=self._verify,
                cert=self._cert,
            )
            r.raise_for_status()
            return self.get_local_repo(repo_name)
        except RepositoryNotFoundException:
            raise

    # Virtual repositories operations
    def create_virtual_repo(self, repo: VirtualRepository) -> VirtualRepositoryResponse:
        """
        Creates a new local repository
        :param repo: VirtualRepository object
        :return: VirtualRepositoryResponse object
        """
        repo_name = repo.key
        try:
            self.get_virtual_repo(repo_name)
            logging.debug(f"Repository {repo_name} already exists")
            raise RepositoryAlreadyExistsException(
                f"Repository {repo_name} already exists"
            )
        except RepositoryNotFoundException:
            request_url = f"{self._artifactory.url}/api/{self._uri}/{repo_name}"
            r = requests.put(
                request_url,
                json=repo.dict(),
                auth=self._auth,
                verify=self._verify,
                cert=self._cert,
            )
            r.raise_for_status()
            return self.get_virtual_repo(repo_name)

    def get_virtual_repo(self, repo_name: str) -> VirtualRepositoryResponse:
        """
        Finds repository in artifactory. Fill object if exist
        :param repo_name: Name of the repository to retrieve
        :return: VirtualRepositoryResponse object
        """
        request_url = f"{self._artifactory.url}/api/{self._uri}/{repo_name}"
        r = requests.get(
            request_url, auth=self._auth, verify=self._verify, cert=self._cert
        )
        if r.status_code == 404 or r.status_code == 400:
            logging.debug(f"Repository {repo_name} does not exist")
            raise RepositoryNotFoundException(f" Repository {repo_name} does not exist")
        else:
            logging.debug(f"Repository {repo_name} exists")
            r.raise_for_status()
            return VirtualRepositoryResponse(**r.json())

    def update_virtual_repo(self, repo: VirtualRepository) -> VirtualRepositoryResponse:
        """
        Updates a virtual artifactory repository
        :param repo: VirtualRepository object
        :return: VirtualRepositoryResponse
        """
        repo_name = repo.key
        try:
            self.get_virtual_repo(repo_name)
            request_url = f"{self._artifactory.url}/api/{self._uri}/{repo_name}"
            r = requests.post(
                request_url,
                json=repo.dict(),
                auth=self._auth,
                verify=self._verify,
                cert=self._cert,
            )
            r.raise_for_status()
            return self.get_virtual_repo(repo_name)
        except RepositoryNotFoundException:
            raise

    # Remote repositories operations
    def create_remote_repo(self, repo: RemoteRepository) -> RemoteRepositoryResponse:
        """
        Creates a new local repository
        :param repo: RemoteRepository object
        :return: RemoteRepositoryResponse object
        """
        repo_name = repo.key
        try:
            self.get_remote_repo(repo_name)
            logging.debug(f"Repository {repo_name} already exists")
            raise RepositoryAlreadyExistsException(
                f"Repository {repo_name} already exists"
            )
        except RepositoryNotFoundException:
            request_url = f"{self._artifactory.url}/api/{self._uri}/{repo_name}"
            r = requests.put(
                request_url,
                json=repo.dict(),
                auth=self._auth,
                verify=self._verify,
                cert=self._cert,
            )
            r.raise_for_status()
            return self.get_remote_repo(repo_name)

    def get_remote_repo(self, repo_name: str) -> RemoteRepositoryResponse:
        """
        Finds a remote repository in artifactory. Fill object if exist
        :param repo_name: Name of the repository to retrieve
        :return: RemoteRepositoryResponse object
        """
        request_url = f"{self._artifactory.url}/api/{self._uri}/{repo_name}"
        r = requests.get(
            request_url, auth=self._auth, verify=self._verify, cert=self._cert
        )
        if r.status_code == 404 or r.status_code == 400:
            logging.debug(f"Repository {repo_name} does not exist")
            raise RepositoryNotFoundException(f" Repository {repo_name} does not exist")
        else:
            logging.debug(f"Repository {repo_name} exists")
            r.raise_for_status()
            return RemoteRepositoryResponse(**r.json())

    def update_remote_repo(self, repo: RemoteRepository) -> RemoteRepositoryResponse:
        """
        Updates a remote artifactory repository
        :param repo: VirtualRepository object
        :return: VirtualRepositoryResponse
        """
        repo_name = repo.key
        try:
            self.get_remote_repo(repo_name)
            request_url = f"{self._artifactory.url}/api/{self._uri}/{repo_name}"
            r = requests.post(
                request_url,
                json=repo.dict(),
                auth=self._auth,
                verify=self._verify,
                cert=self._cert,
            )
            r.raise_for_status()
            return self.get_remote_repo(repo_name)
        except RepositoryNotFoundException:
            raise

    def list(self) -> List[SimpleRepository]:
        """
        Lists all the repositories
        :return: A list of repositories
        """
        request_url = f"{self._artifactory.url}/api/{self._uri}"
        r = requests.get(
            request_url, auth=self._auth, verify=self._verify, cert=self._cert
        )
        r.raise_for_status()

        repositories_list = []
        for repository in r.json():
            repositories_list.append(SimpleRepository(**repository))

        return repositories_list

    def delete(self, repo_name: str) -> None:
        """
        Removes a local repository
        :param repo_name: Name of the repository to delete
        :return: None
        """
        try:
            request_url = f"{self._artifactory.url}/api/{self._uri}/{repo_name}"
            r = requests.delete(
                request_url, auth=self._auth, verify=self._verify, cert=self._cert
            )
            r.raise_for_status()
        except requests.exceptions.HTTPError:
            raise


class ArtifactoryPermission(ArtifactoryAuth):
    _uri = "security/permissions"

    def __init__(self, artifactory: AuthModel) -> None:
        super(ArtifactoryPermission, self).__init__(artifactory)

    def create(self, permission: Permission) -> Permission:
        """
        Creates a permission
        :param permission: Permission object
        :return: Permission
        """
        permission_name = permission.name
        try:
            self.get(permission_name)
            logging.debug(f"Permission {permission_name} already exists")
            raise PermissionAlreadyExistsException(
                f"Permission {permission_name} already exists"
            )
        except PermissionNotFoundException:
            request_url = f"{self._artifactory.url}/api/{self._uri}/{permission_name}"
            r = requests.put(
                request_url,
                json=permission.dict(),
                auth=self._auth,
                verify=self._verify,
                cert=self._cert,
            )
            r.raise_for_status()
            return self.get(permission_name)

    def get(self, permission_name: str) -> Permission:
        """
        Read permission from artifactory. Fill object if exist
        :param permission_name: Name of the permission to retrieve
        :return: Permission
        """
        request_url = f"{self._artifactory.url}/api/{self._uri}/{permission_name}"
        r = requests.get(
            request_url, auth=self._auth, verify=self._verify, cert=self._cert
        )
        if r.status_code == 404 or r.status_code == 400:
            logging.debug(f"Permission {permission_name} does not exist")
            raise PermissionNotFoundException(
                f"Permission {permission_name} does not exist"
            )
        else:
            logging.debug(f"Permission {permission_name} exists")
            r.raise_for_status()
            return Permission(**r.json())

    def list(self) -> List[SimplePermission]:
        """
        Lists all the permissions
        :return: A list of permissions
        """
        request_url = f"{self._artifactory.url}/api/{self._uri}"
        r = requests.get(
            request_url, auth=self._auth, verify=self._verify, cert=self._cert
        )
        r.raise_for_status()

        permissions_list = []
        for permission in r.json():
            permissions_list.append(SimplePermission(**permission))

        return permissions_list

    def update(self, permission: Permission) -> Permission:
        """
        Updates an artifactory permission
        :param permission: Permission object
        :return: Permission
        """
        return self.create(permission)

    def delete(self, permission_name: str) -> None:
        """
        Removes an artifactory permission
        :param permission_name: Name of the permission to delete
        :return: None
        """
        self.get(permission_name)
        request_url = f"{self._artifactory.url}/api/{self._uri}/{permission_name}"
        r = requests.delete(
            request_url, auth=self._auth, verify=self._verify, cert=self._cert
        )
        r.raise_for_status()
