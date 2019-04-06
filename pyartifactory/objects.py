import logging

import requests

from pyartifactory.exception import UserNotFoundException, UserAlreadyExistsException
from pyartifactory.models.Artifactory import ArtifactoryModel
from pyartifactory.models.User import User, NewUser, UserList


class ArtfictoryUser:
    _uri = "security/users"

    def __init__(self, artifactory: ArtifactoryModel):
        self.artifactory = artifactory
        self.auth = (
            self.artifactory.auth[0],
            self.artifactory.auth[1].get_secret_value(),
        )

    def create(self, user: NewUser) -> User:
        """
        Create user
        :return: User
        """
        try:
            self.get(user.name)
            logging.debug(f"User {user.name} already exists")
            raise UserAlreadyExistsException(f"User {user.name} already exists")
        except UserNotFoundException:
            request_url = f"{self.artifactory.url}/api/{self._uri}/{self.artifactory.name}"
            r = requests.put(request_url, json=user.dict(), auth=self.artifactory.auth)
            r.raise_for_status()
            return self.get(r.json().get("name"))

    def get(self, name: str) -> User:
        """
        Read user from artifactory. Fill object if exist
        :return: UserModel
        """
        request_url = f"{self.artifactory.url}/api/{self._uri}/{name}"
        r = requests.get(request_url, auth=self.auth)
        if 404 == r.status_code == r.status_code:
            logging.debug(f"User {name} does not exist")
            raise UserNotFoundException(f"{name} does not exist")
        else:
            logging.debug(f"User {name} exists")
            r.raise_for_status()
            return User(**r.json())

    def list(self) -> UserList:
        """
        List all the users
        :return: UserList
        """
        request_url = f"{self.artifactory.url}/api/{self._uri}"
        r = requests.get(request_url, auth=self.auth)
        r.raise_for_status()
        return UserList(users=r.json())

    def update(self, user: NewUser) -> User:
        """
        Update user
        :return: UserModel
        """
        try:
            self.get(user.name)
            request_url = f"{self.artifactory.url}/api/{self._uri}/{user.name}"
            r = requests.post(request_url, json=user.dict(), auth=self.auth)
            r.raise_for_status()
            return self.get(r.json().get("name"))
        except UserNotFoundException:
            raise

    def delete(self, name: str) -> None:
        """
        Remove user
        :return: None
        """
        request_url = f"{self.artifactory.url}/api/{self._uri}/{name}"
        r = requests.delete(request_url, auth=self.auth)
        r.raise_for_status()
