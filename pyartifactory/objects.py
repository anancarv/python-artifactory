import logging

import requests

from pyartifactory.exception import (
    UserNotFoundException,
    UserAlreadyExistsException,
    GroupNotFoundException,
)
from pyartifactory.models.Auth import AuthModel, ApiKeyModel, PasswordModel
from pyartifactory.models.Group import Group, GroupList
from pyartifactory.models.User import User, NewUser, UserList


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

    def create(self, user: NewUser) -> User:
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

    def get(self, name: str) -> User:
        """
        Read user from artifactory. Fill object if exist
        :param name: Name of the user to retrieve
        :return: UserModel
        """
        request_url = f"{self._artifactory.url}/api/{self._uri}/{name}"
        r = requests.get(
            request_url, auth=self._auth, verify=self._verify, cert=self._cert
        )
        if 404 == r.status_code == r.status_code:
            logging.debug(f"User {name} does not exist")
            raise UserNotFoundException(f"{name} does not exist")
        else:
            logging.debug(f"User {name} exists")
            r.raise_for_status()
            return User(**r.json())

    def list(self) -> UserList:
        """
        Lists all the users
        :return: UserList
        """
        request_url = f"{self._artifactory.url}/api/{self._uri}"
        r = requests.get(
            request_url, auth=self._auth, verify=self._verify, cert=self._cert
        )
        r.raise_for_status()
        return UserList(users=r.json())

    def update(self, user: NewUser) -> User:
        """
        Updates an artifactory user
        :param user: NewUser object
        :return: UserModel
        """
        username = user.name
        try:
            self.get(username)
            request_url = f"{self._artifactory.url}/api/{self._uri}/{username}"
            r = requests.post(
                request_url,
                json=user.dict(),
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
        request_url = f"{self._artifactory.url}/api/{self._uri}/{name}"
        r = requests.delete(
            request_url, auth=self._auth, verify=self._verify, cert=self._cert
        )
        r.raise_for_status()


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
            raise UserAlreadyExistsException(f"Group {group_name} already exists")
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
        if 404 == r.status_code == r.status_code:
            logging.debug(f"Group {name} does not exist")
            raise GroupNotFoundException(f"Group {name} does not exist")
        else:
            logging.debug(f"Group {name} exists")
            r.raise_for_status()
            return Group(**r.json())

    def list(self) -> GroupList:
        """
        Lists all the groups
        :return: GroupList
        """
        request_url = f"{self._artifactory.url}/api/{self._uri}"
        r = requests.get(
            request_url, auth=self._auth, verify=self._verify, cert=self._cert
        )
        r.raise_for_status()
        return GroupList(groups=r.json())

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
        request_url = f"{self._artifactory.url}/api/{self._uri}/{name}"
        r = requests.delete(
            request_url, auth=self._auth, verify=self._verify, cert=self._cert
        )
        r.raise_for_status()
