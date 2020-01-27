import json
import logging
from typing import List, Optional, Dict, Tuple, Union

import requests
from requests import Response
from requests_toolbelt.multipart import encoder
from pathlib import Path

from pyartifactory.exception import (
    UserNotFoundException,
    UserAlreadyExistsException,
    GroupNotFoundException,
    RepositoryAlreadyExistsException,
    GroupAlreadyExistsException,
    RepositoryNotFoundException,
    ArtifactoryException,
    PermissionAlreadyExistsException,
    PermissionNotFoundException,
    InvalidTokenDataException,
    AqlException,
)

from pyartifactory.models import (
    AuthModel,
    ApiKeyModel,
    PasswordModel,
    AccessTokenModel,
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
    User,
    Permission,
    SimplePermission,
    ArtifactPropertiesResponse,
    ArtifactStatsResponse,
    Aql,
)


class Artifactory:
    def __init__(
        self,
        url: str,
        auth: Tuple[str, str] = None,
        verify: bool = True,
        cert: str = None,
    ):
        self.artifactory = AuthModel(url=url, auth=auth, verify=verify, cert=cert)
        self.users = ArtifactoryUser(self.artifactory)
        self.groups = ArtifactoryGroup(self.artifactory)
        self.security = ArtifactorySecurity(self.artifactory)
        self.repositories = ArtifactoryRepository(self.artifactory)
        self.artifacts = ArtifactoryArtifact(self.artifactory)
        self.aql = ArtifactoryAql(self.artifactory)


class ArtifactoryObject:
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
        self, method: str, route: str, raise_for_status: bool = True, **kwargs
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
        if raise_for_status:
            response.raise_for_status()
        return response


class ArtifactoryUser(ArtifactoryObject):
    _uri = "security/users"

    def __init__(self, artifactory: AuthModel) -> None:
        super(ArtifactoryUser, self).__init__(artifactory)

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
            logging.debug(f"User {username} successfully created")
            return self.get(user.name)

    def get(self, name: str) -> UserResponse:
        """
        Read user from artifactory. Fill object if exist
        :param name: Name of the user to retrieve
        :return: UserModel
        """
        try:
            r = self._get(f"api/{self._uri}/{name}")
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
        logging.debug("List all users successful")
        return [SimpleUser(**user) for user in r.json()]

    def update(self, user: User) -> UserResponse:
        """
        Updates an artifactory user
        :param user: NewUser object
        :return: UserModel
        """
        username = user.name
        self.get(username)
        self._post(f"api/{self._uri}/{username}", json=user.dict())
        logging.debug(f"User {username} successfully updated")
        return self.get(username)

    def delete(self, name: str) -> None:
        """
        Remove user
        :param name: Name of the user to delete
        :return: None
        """
        self.get(name)
        self._delete(f"api/{self._uri}/{name}")
        logging.debug(f"User {name} successfully deleted")


class ArtifactorySecurity(ArtifactoryObject):
    _uri = "security"

    def __init__(self, artifactory: AuthModel) -> None:
        super(ArtifactorySecurity, self).__init__(artifactory)

    def get_encrypted_password(self) -> PasswordModel:
        """
        Get the encrypted password of the authenticated requestor.
        :return: str
        """
        response = self._get(f"api/{self._uri}/encryptedPassword")
        logging.debug("Encrypted password successfully delivered")
        return PasswordModel(**response.json())

    def create_access_token(
        self,
        user_name: str,
        expires_in: int = 3600,
        refreshable: bool = False,
        groups: Optional[List[str]] = None,
    ) -> AccessTokenModel:
        """
        Creates an access token.

        :param user_name: Name of the user to whom an access key should be granted. transient token created if
                          user doesn't exist in artifactory.
        :param expires_in: Expiry time for the token in seconds. For eternal tokens specify 0.
        :param refreshable: If set to true token can be refreshed using the refresh token returned. defaults False.
        :param groups: A list of groups the token has membership of. If an existing user in artifactory is used with
                       existing memberships those groups are automatically implied without specification.
        :return: AccessToken
        """
        payload = {
            "username": user_name,
            "expires_in": expires_in,
            "refreshable": refreshable,
        }
        if groups:
            if not isinstance(groups, list):
                raise ValueError(groups)
            scope = f'member-of-groups:"{", ".join(groups)}"'
            payload.update({"scope": scope})
        response = self._post(
            f"api/{self._uri}/token", data=payload, raise_for_status=False
        )
        if response.ok:
            return AccessTokenModel(**response.json())
        raise InvalidTokenDataException(
            response.json().get("error_description", "Unknown error")
        )

    def revoke_access_token(self, token: str = None, token_id: str = None) -> bool:
        """
        Revokes an access token.

        :param token: The token to revoke
        :param token_id: The id of a token to revoke
        :return: bool True or False indicating success or failure of token revocation attempt.
        """
        if not any([token, token_id]):
            logging.error("Neither a token or a token id was specified")
            raise InvalidTokenDataException
        payload: Dict[str, Optional[str]] = {"token": token} if token else {
            "token_id": token_id
        }
        response = self._post(
            f"api/{self._uri}/token/revoke", data=payload, raise_for_status=False
        )
        if response.ok:
            logging.info("Token revoked successfully, or token did not exist")
            return True
        logging.error("Token revocation unsuccessful, response was %s", response.text)
        return False

    def create_api_key(self) -> ApiKeyModel:
        """
        Create an API key for the current user.
        :return: Error if API key already exists - use regenerate API key instead.
        """
        r = self._post(f"api/{self._uri}/apiKey")
        logging.debug(f"API Key successfully created")
        return ApiKeyModel(**r.json())

    def regenerate_api_key(self) -> ApiKeyModel:
        """
        Regenerate an API key for the current user
        :return: API key
        """
        r = self._put(f"api/{self._uri}/apiKey")
        logging.debug(f"API Key successfully regenerated")
        return ApiKeyModel(**r.json())

    def get_api_key(self) -> ApiKeyModel:
        """
        Get the current user's own API key
        :return: API key
        """
        r = self._get(f"api/{self._uri}/apiKey")
        logging.debug(f"API Key successfully delivered")
        return ApiKeyModel(**r.json())

    def revoke_api_key(self) -> None:
        """
        Revokes the current user's API key
        :return: None
        """
        self._delete(f"api/{self._uri}/apiKey")
        logging.debug(f"API Key successfully revoked")

    def revoke_user_api_key(self, name: str) -> None:
        """
        Revokes the API key of another user
        :param name: name of the user to whom api key has to be revoked
        :return: None
        """
        self._delete(f"api/{self._uri}/apiKey/{name}")
        logging.debug(f"User API Key successfully revoked")


class ArtifactoryGroup(ArtifactoryObject):
    _uri = "security/groups"

    def __init__(self, artifactory: AuthModel) -> None:
        super(ArtifactoryGroup, self).__init__(artifactory)

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
            logging.debug(f"Group {group_name} successfully created")
            return self.get(group.name)

    def get(self, name: str) -> Group:
        """
        Get the details of an Artifactory Group
        :param name: Name of the group to retrieve
        :return: Found artifactory group
        """
        try:
            r = self._get(f"api/{self._uri}/{name}")
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
        logging.debug("List all groups successful")
        return [Group(**group) for group in r.json()]

    def update(self, group: Group) -> Group:
        """
        Updates an exiting group in Artifactory with the provided group details.
        :param group: Group to be updated
        :return: Updated group
        """
        group_name = group.name
        self.get(group_name)
        self._post(f"api/{self._uri}/{group_name}", json=group.dict())
        logging.debug(f"Group {group_name} successfully updated")
        return self.get(group_name)

    def delete(self, name: str) -> None:
        """
        Removes a group
        :param name: Name of the group to delete
        :return: None
        """
        self.get(name)
        self._delete(f"api/{self._uri}/{name}")
        logging.debug(f"Group {name} successfully deleted")


class ArtifactoryRepository(ArtifactoryObject):
    _uri = "repositories"

    def __init__(self, artifactory: AuthModel) -> None:
        super(ArtifactoryRepository, self).__init__(artifactory)

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
            logging.debug(f"Repository {repo_name} successfully created")
            return self.get_local_repo(repo_name)

    def get_local_repo(self, repo_name: str) -> LocalRepositoryResponse:
        """
        Finds repository in artifactory. Fill object if exist
        :param repo_name: Name of the repository to retrieve
        :return: LocalRepositoryResponse object
        """
        try:
            r = self._get(f"api/{self._uri}/{repo_name}")
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
        self.get_local_repo(repo_name)
        self._post(f"api/{self._uri}/{repo_name}", json=repo.dict())
        logging.debug(f"Repository {repo_name} successfully updated")
        return self.get_local_repo(repo_name)

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
            logging.debug(f"Repository {repo_name} successfully created")
            return self.get_virtual_repo(repo_name)

    def get_virtual_repo(self, repo_name: str) -> VirtualRepositoryResponse:
        """
        Finds repository in artifactory. Fill object if exist
        :param repo_name: Name of the repository to retrieve
        :return: VirtualRepositoryResponse object
        """
        try:
            r = self._get(f"api/{self._uri}/{repo_name}")
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
        self.get_virtual_repo(repo_name)
        self._post(f"api/{self._uri}/{repo_name}", json=repo.dict())
        logging.debug(f"Repository {repo_name} successfully updated")
        return self.get_virtual_repo(repo_name)

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
            logging.debug(f"Repository {repo_name} successfully created")
            return self.get_remote_repo(repo_name)

    def get_remote_repo(self, repo_name: str) -> RemoteRepositoryResponse:
        """
        Finds a remote repository in artifactory. Fill object if exist
        :param repo_name: Name of the repository to retrieve
        :return: RemoteRepositoryResponse object
        """
        try:
            r = self._get(f"api/{self._uri}/{repo_name}")
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
        self.get_remote_repo(repo_name)
        self._post(f"api/{self._uri}/{repo_name}", json=repo.dict())
        logging.debug(f"Repository {repo_name} successfully updated")
        return self.get_remote_repo(repo_name)

    def list(self) -> List[SimpleRepository]:
        """
        Lists all the repositories
        :return: A list of repositories
        """
        r = self._get(f"api/{self._uri}")
        logging.debug("List all repositories successful")
        return [SimpleRepository(**repository) for repository in r.json()]

    def delete(self, repo_name: str) -> None:
        """
        Removes a local repository
        :param repo_name: Name of the repository to delete
        :return: None
        """

        self._delete(f"api/{self._uri}/{repo_name}")
        logging.debug(f"Repository {repo_name} successfully deleted")


class ArtifactoryPermission(ArtifactoryObject):
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
            self._put(f"api/{self._uri}/{permission_name}", json=permission.dict())
            logging.debug(f"Permission {permission_name} successfully created")
            return self.get(permission_name)

    def get(self, permission_name: str) -> Permission:
        """
        Read permission from artifactory. Fill object if exist
        :param permission_name: Name of the permission to retrieve
        :return: Permission
        """
        try:
            r = self._get(f"api/{self._uri}/{permission_name}")
            return Permission(**r.json())
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404 or e.response.status_code == 400:
                logging.error(f"Permission {permission_name} does not exist")
                raise PermissionNotFoundException(
                    f"Permission {permission_name} does not exist"
                )
            raise ArtifactoryException from e

    def list(self) -> List[SimplePermission]:
        """
        Lists all the permissions
        :return: A list of permissions
        """
        r = self._get(f"api/{self._uri}")
        logging.debug("List all permissions successful")
        return [SimplePermission(**permission) for permission in r.json()]

    def update(self, permission: Permission) -> Permission:
        """
        Updates an artifactory permission
        :param permission: Permission object
        :return: Permission
        """
        permission_name = permission.name
        self._put(f"api/{self._uri}/{permission_name}", json=permission.dict())
        logging.debug(f"Permission {permission_name} successfully updated")
        return self.get(permission_name)

    def delete(self, permission_name: str) -> None:
        """
        Removes an artifactory permission
        :param permission_name: Name of the permission to delete
        :return: None
        """
        self.get(permission_name)
        self._delete(f"api/{self._uri}/{permission_name}")
        logging.debug(f"Permission {permission_name} successfully deleted")


class ArtifactoryArtifact(ArtifactoryObject):
    def __init__(self, artifactory: AuthModel) -> None:
        super(ArtifactoryArtifact, self).__init__(artifactory)

    def deploy(
        self, local_file_location: str, artifact_path: str
    ) -> ArtifactPropertiesResponse:
        """
        :param artifact_path: Path to file in Artifactory
        :param local_file_location: Location of the file to deploy
        """
        artifact_path = artifact_path.lstrip("/")
        local_filename = artifact_path.split("/")[-1]
        with open(local_file_location, "rb") as f:
            form = encoder.MultipartEncoder(
                {
                    "documents": (local_filename, f, "application/octet-stream"),
                    "composite": "NONE",
                }
            )
            headers = {"Prefer": "respond-async", "Content-Type": form.content_type}
            self._put(f"{artifact_path}", headers=headers, data=form)
            logging.info(f"Artifact {local_filename} successfully deployed")
            return self.properties(artifact_path)

    def download(self, artifact_path: str, local_directory_path: str = None) -> str:
        """
        :param artifact_path: Path to file in Artifactory
        :param local_directory_path: Local path to where the artifact will be imported
        :return: File name
        """
        artifact_path = artifact_path.lstrip("/")
        local_filename = artifact_path.split("/")[-1]

        if local_directory_path:
            Path(local_directory_path).mkdir(parents=True, exist_ok=True)
            local_file_full_path = f"{local_directory_path}/{local_filename}"
        else:
            local_file_full_path = local_filename

        with self._get(f"{artifact_path}", stream=True) as r:
            with open(local_file_full_path, "wb") as f:
                for chunk in r.iter_content(chunk_size=8192):
                    if chunk:  # filter out keep-alive new chunks
                        f.write(chunk)
                        # f.flush()
        logging.info(f"Artifact {local_filename} successfully downloaded")
        return local_file_full_path

    def properties(self, artifact_path: str) -> ArtifactPropertiesResponse:
        """
        :param artifact_path: Path to file in Artifactory
        :return: Artifact properties
        """
        artifact_path = artifact_path.lstrip("/")
        r = self._get(f"api/storage/{artifact_path}?properties[=x[,y]]")
        logging.info("Artifact Properties successfully retrieved")
        return ArtifactPropertiesResponse(**r.json())

    def stats(self, artifact_path: str) -> ArtifactStatsResponse:
        """
        :param artifact_path: Path to file in Artifactory
        :return: Artifact Stats
        """
        artifact_path = artifact_path.lstrip("/")
        r = self._get(f"api/storage/{artifact_path}?stats")
        logging.info("Artifact stats successfully retrieved")
        return ArtifactStatsResponse(**r.json())

    def copy(
        self, artifact_current_path: str, artifact_new_path: str, dryrun: bool = False
    ) -> ArtifactPropertiesResponse:
        """
        :param artifact_current_path: Current path to file
        :param artifact_new_path: New path to file
        :param dryrun: Dry run
        :return: ArtifactPropertiesResponse: properties of the copied artifact
        """
        artifact_current_path = artifact_current_path.lstrip("/")
        artifact_new_path = artifact_new_path.lstrip("/")
        if dryrun:
            dry = 1
        else:
            dry = 0

        self._post(f"api/copy/{artifact_current_path}?to={artifact_new_path}&dry={dry}")
        logging.info(f"Artifact {artifact_current_path} successfully copied")
        return self.properties(artifact_new_path)

    def move(
        self, artifact_current_path: str, artifact_new_path: str, dryrun: bool = False
    ) -> ArtifactPropertiesResponse:
        """
        :param artifact_current_path: Current path to file
        :param artifact_new_path: New path to file
        :param dryrun: Dry run
        :return: ArtifactPropertiesResponse: properties of the moved artifact
        """
        artifact_current_path = artifact_current_path.lstrip("/")
        artifact_new_path = artifact_new_path.lstrip("/")

        if dryrun:
            dry = 1
        else:
            dry = 0

        self._post(f"api/move/{artifact_current_path}?to={artifact_new_path}&dry={dry}")
        logging.info(f"Artifact {artifact_current_path} successfully moved")
        return self.properties(artifact_new_path)

    def delete(self, artifact_path: str) -> None:
        """
        :param artifact_path: Path to file in Artifactory
        :return: bool
        """
        artifact_path = artifact_path.lstrip("/")
        self._delete(f"{artifact_path}")
        logging.info(f"Artifact {artifact_path} successfully deleted")


def create_aql_query(aql_object: Aql):
    aql_query_text = f"{aql_object.domain}.find"

    if aql_object.find:
        aql_query_text += f"({json.dumps(aql_object.find)})"
    else:
        aql_query_text += "()"

    if aql_object.include:
        format_include = (
            json.dumps(aql_object.include).replace("[", "").replace("]", "")
        )
        aql_query_text += f".include({format_include})"

    if aql_object.sort:
        sort_key = list(aql_object.sort.keys())[0]
        sort_value = json.dumps(aql_object.sort[sort_key])
        aql_query_text += f'.sort({{"{sort_key.value}": {sort_value}}})'

    if aql_object.offset:
        aql_query_text += f".offset({aql_object.offset})"

    if aql_object.limit:
        aql_query_text += f".limit({aql_object.limit})"

    return aql_query_text


class ArtifactoryAql(ArtifactoryObject):
    _uri = "search/aql"

    def __init__(self, artifactory: AuthModel) -> None:
        super(ArtifactoryAql, self).__init__(artifactory)

    def query(self, aql_object: Aql) -> List[Dict[str, Union[str, List]]]:
        aql_query = create_aql_query(aql_object)
        try:
            response = self._post(f"api/{self._uri}", data=aql_query)
            return response.json()["results"]
        except requests.exceptions.HTTPError:
            raise AqlException(
                "Bad Aql Query: please check your parameters."
                "Doc: https://www.jfrog.com/confluence/display/RTF/Artifactory+Query+Language"
            )
