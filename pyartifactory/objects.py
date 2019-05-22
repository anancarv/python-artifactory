import logging
from typing import List

import requests
from requests import Response

from pyartifactory.exception import (
    UserNotFoundException,
    UserAlreadyExistsException,
    GroupNotFoundException,
    RepositoryAlreadyExistsException,
    GroupAlreadyExistsException,
    RepositoryNotFoundException,
    ArtifactoryException,
)
from pyartifactory.models import (
    AuthModel,
    ApiKeyModel,
    PasswordModel,
    Group,
    LocalRepository,
    VirtualRepository,
    LocalRepositoryResponse,
    VirtualRepositoryResponse,
    RemoteRepository,
    RemoteRepositoryResponse,
    SimpleRepository,
    UserResponse,
    NewUser,
    SimpleUser,
)


class ArtifactoryAuth:
    def __init__(self, artifactory: AuthModel) -> None:
        self._artifactory = artifactory
        self._auth = (
            self._artifactory.auth[0],
            self._artifactory.auth[1].get_secret_value(),
        )
        self._verify = self._artifactory.verify
        self._cert = self._artifactory.cert
        self.session = requests.Session()

    def _get(self, route: str, **kwargs) -> Response:
        """
        :param route: API Route
        :param kwargs: Additional parameters to add the request
        :returns  An HTTP response
        """
        return self._generic_http_method_request("get", route, **kwargs)

    def _post(self, route: str, **kwargs) -> Response:
        """
        :param route: API Route
        :param kwargs: Additional parameters to add the request
        :returns  An HTTP response
        """
        return self._generic_http_method_request("post", route, **kwargs)

    def _put(self, route: str, **kwargs) -> Response:
        """
        :param route: API Route
        :param kwargs: Additional parameters to add the request
        :returns  An HTTP response
        """
        return self._generic_http_method_request("put", route, **kwargs)

    def _delete(self, route: str, **kwargs) -> Response:
        """
        :param route: API Route
        :param kwargs: Additional parameters to add the request
        :returns  An HTTP response
        """
        return self._generic_http_method_request("delete", route, **kwargs)

    def _generic_http_method_request(
        self, method: str, route: str, **kwargs
    ) -> Response:
        """
        :param method: HTTP method to use
        :param route: API Route
        :param kwargs: Additional parameters to add the request
        :return: An HTTP response
        """
        http_method = getattr(self.session, method)
        response = http_method(
            f"{self._artifactory.url}/{route}",
            auth=self._auth,
            **kwargs,
            verify=self._verify,
            cert=self._cert,
        )

        response.raise_for_status()
        return response


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
            logging.error(f"User {username} already exists")
            raise UserAlreadyExistsException(f"User {username} already exists")
        except UserNotFoundException:
            data = user.dict()
            data["password"] = user.password.get_secret_value()
            self._put(f"api/{self._uri}/{username}", json=data)
            logging.info(f"User {username} successfully created")
            return self.get(user.name)

    def get(self, name: str) -> UserResponse:
        """
        Read user from artifactory. Fill object if exist
        :param name: Name of the user to retrieve
        :return: UserModel
        """
        try:
            r = self._get(f"api/{self._uri}/{name}")
            logging.info(f"User {name} exists")
            return UserResponse(**r.json())
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404 or e.response.status_code == 400:
                logging.error(f"User {name} does not exist")
                raise UserNotFoundException(f"{name} does not exist")
            raise ArtifactoryException from e

    def list(self) -> List[SimpleUser]:
        """
        Lists all the users
        :return: UserList
        """
        r = self._get(f"api/{self._uri}")
        logging.info("List all users successful")
        return [SimpleUser(**user) for user in r.json()]

    def update(self, user: NewUser) -> UserResponse:
        """
        Updates an artifactory user
        :param user: NewUser object
        :return: UserModel
        """
        username = user.name
        try:
            self.get(username)
            data = user.dict()
            data["password"] = user.password.get_secret_value()
            self._post(f"api/{self._uri}/{username}", json=data)
            logging.info(f"User {username} successfully updated")
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
            self._delete(f"api/{self._uri}/{name}")
            logging.info(f"User {name} successfully deleted")
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
        r = self._get(f"api/{self._uri}/encryptedPassword")
        logging.info(f"Encrypted password successfully delivered")
        return PasswordModel(**r.json())

    def create_api_key(self) -> ApiKeyModel:
        """
        Create an API key for the current user.
        :return: Error if API key already exists - use regenerate API key instead.
        """
        r = self._post(f"api/{self._uri}/apiKey")
        logging.info(f"API Key successfully created")
        return ApiKeyModel(**r.json())

    def regenerate_api_key(self) -> ApiKeyModel:
        """
        Regenerate an API key for the current user
        :return: API key
        """
        r = self._put(f"api/{self._uri}/apiKey")
        logging.info(f"API Key successfully regenerated")
        return ApiKeyModel(**r.json())

    def get_api_key(self) -> ApiKeyModel:
        """
        Get the current user's own API key
        :return: API key
        """
        r = self._get(f"api/{self._uri}/apiKey")
        logging.info(f"API Key successfully delivered")
        return ApiKeyModel(**r.json())

    def revoke_api_key(self) -> None:
        """
        Revokes the current user's API key
        :return: None
        """
        self._delete(f"api/{self._uri}/apiKey")
        logging.info(f"API Key successfully revoked")

    def revoke_user_api_key(self, name: str) -> None:
        """
        Revokes the API key of another user
        :param name: name of the user to whom api key has to be revoked
        :return: None
        """
        self._delete(f"api/{self._uri}/apiKey/{name}")
        logging.info(f"User API Key successfully revoked")


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
            logging.error(f"Group {group_name} already exists")
            raise GroupAlreadyExistsException(f"Group {group_name} already exists")
        except GroupNotFoundException:
            self._put(f"api/{self._uri}/{group_name}", json=group.dict())
            logging.info(f"Group {group_name} successfully created")
            return self.get(group.name)

    def get(self, name: str) -> Group:
        """
        Get the details of an Artifactory Group
        :param name: Name of the group to retrieve
        :return: Found artifactory group
        """
        try:
            r = self._get(f"api/{self._uri}/{name}")
            logging.info(f"Group {name} exists")
            return Group(**r.json())
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404 or e.response.status_code == 400:
                logging.error(f"Group {name} does not exist")
                raise GroupNotFoundException(f"Group {name} does not exist")
            raise ArtifactoryException from e

    def list(self) -> List[Group]:
        """
        Lists all the groups
        :return: GroupList
        """
        r = self._get(f"api/{self._uri}")
        logging.info("List all groups successful")
        return [Group(**group) for group in r.json()]

    def update(self, group: Group) -> Group:
        """
        Updates an exiting group in Artifactory with the provided group details.
        :param group: Group to be updated
        :return: Updated group
        """
        group_name = group.name
        try:
            self.get(group_name)
            self._post(f"api/{self._uri}/{group_name}", json=group.dict())
            logging.info(f"Group {group_name} successfully updated")
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
            self._delete(f"api/{self._uri}/{name}")
            logging.info(f"Group {name} successfully deleted")
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
            logging.error(f"Repository {repo_name} already exists")
            raise RepositoryAlreadyExistsException(
                f"Repository {repo_name} already exists"
            )
        except RepositoryNotFoundException:
            self._put(f"api/{self._uri}/{repo_name}", json=repo.dict())
            logging.info(f"Repository {repo_name} successfully created")
            return self.get_local_repo(repo_name)

    def get_local_repo(self, repo_name: str) -> LocalRepositoryResponse:
        """
        Finds repository in artifactory. Fill object if exist
        :param repo_name: Name of the repository to retrieve
        :return: LocalRepositoryResponse object
        """
        try:
            r = self._get(f"api/{self._uri}/{repo_name}")
            logging.info(f"Repository {repo_name} exists")
            return LocalRepositoryResponse(**r.json())
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404 or e.response.status_code == 400:
                logging.error(f"Repository {repo_name} does not exist")
                raise RepositoryNotFoundException(
                    f" Repository {repo_name} does not exist"
                )
            raise ArtifactoryException from e

    def update_local_repo(self, repo: LocalRepository) -> LocalRepositoryResponse:
        """
        Updates an artifactory repository
        :param repo: LocalRepository object
        :return: LocalRepositoryResponse
        """
        repo_name = repo.key
        try:
            self.get_local_repo(repo_name)
            self._post(f"api/{self._uri}/{repo_name}", json=repo.dict())
            logging.info(f"Repository {repo_name} successfully updated")
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
            logging.error(f"Repository {repo_name} already exists")
            raise RepositoryAlreadyExistsException(
                f"Repository {repo_name} already exists"
            )
        except RepositoryNotFoundException:
            self._put(f"api/{self._uri}/{repo_name}", json=repo.dict())
            logging.info(f"Repository {repo_name} successfully created")
            return self.get_virtual_repo(repo_name)

    def get_virtual_repo(self, repo_name: str) -> VirtualRepositoryResponse:
        """
        Finds repository in artifactory. Fill object if exist
        :param repo_name: Name of the repository to retrieve
        :return: VirtualRepositoryResponse object
        """
        try:
            r = self._get(f"api/{self._uri}/{repo_name}")
            logging.info(f"Repository {repo_name} exists")
            return VirtualRepositoryResponse(**r.json())
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404 or e.response.status_code == 400:
                logging.error(f"Repository {repo_name} does not exist")
                raise RepositoryNotFoundException(
                    f" Repository {repo_name} does not exist"
                )
            raise ArtifactoryException from e

    def update_virtual_repo(self, repo: VirtualRepository) -> VirtualRepositoryResponse:
        """
        Updates a virtual artifactory repository
        :param repo: VirtualRepository object
        :return: VirtualRepositoryResponse
        """
        repo_name = repo.key
        try:
            self.get_virtual_repo(repo_name)
            self._post(f"api/{self._uri}/{repo_name}", json=repo.dict())
            logging.info(f"Repository {repo_name} successfully updated")
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
            logging.error(f"Repository {repo_name} already exists")
            raise RepositoryAlreadyExistsException(
                f"Repository {repo_name} already exists"
            )
        except RepositoryNotFoundException:
            self._put(f"api/{self._uri}/{repo_name}", json=repo.dict())
            logging.info(f"Repository {repo_name} successfully created")
            return self.get_remote_repo(repo_name)

    def get_remote_repo(self, repo_name: str) -> RemoteRepositoryResponse:
        """
        Finds a remote repository in artifactory. Fill object if exist
        :param repo_name: Name of the repository to retrieve
        :return: RemoteRepositoryResponse object
        """
        try:
            r = self._get(f"api/{self._uri}/{repo_name}")
            logging.info(f"Repository {repo_name} exists")
            return RemoteRepositoryResponse(**r.json())
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404 or e.response.status_code == 400:
                logging.error(f"Repository {repo_name} does not exist")
                raise RepositoryNotFoundException(
                    f" Repository {repo_name} does not exist"
                )
            raise ArtifactoryException from e

    def update_remote_repo(self, repo: RemoteRepository) -> RemoteRepositoryResponse:
        """
        Updates a remote artifactory repository
        :param repo: VirtualRepository object
        :return: VirtualRepositoryResponse
        """
        repo_name = repo.key
        try:
            self.get_remote_repo(repo_name)
            self._post(f"api/{self._uri}/{repo_name}", json=repo.dict())
            logging.info(f"Repository {repo_name} successfully updated")
            return self.get_remote_repo(repo_name)
        except RepositoryNotFoundException:
            raise

    def list(self) -> List[SimpleRepository]:
        """
        Lists all the repositories
        :return: A list of repositories
        """
        r = self._get(f"api/{self._uri}")
        logging.info("List all repositories successful")
        return [SimpleRepository(**repository) for repository in r.json()]

    def delete(self, repo_name: str) -> None:
        """
        Removes a local repository
        :param repo_name: Name of the repository to delete
        :return: None
        """
        try:
            self._delete(f"api/{self._uri}/{repo_name}")
            logging.info(f"Repository {repo_name} successfully deleted")
        except RepositoryNotFoundException:
            raise


class ArtfictoryPermission(ArtifactoryAuth):
    _uri = "permissions"

    def __init__(self, artifactory: AuthModel) -> None:
        super(ArtfictoryPermission, self).__init__(artifactory)

    def create(self):
        # ToDo
        pass

    def get(self):
        # ToDo
        pass

    def update(self):
        # ToDo
        pass

    def delete(self):
        # ToDo
        pass
