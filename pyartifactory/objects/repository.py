from __future__ import annotations

import json
import logging
from typing import List, Union, overload

import requests
from pydantic import ValidationError
from requests import Response

from pyartifactory.exception import ArtifactoryError, RepositoryAlreadyExistsError, RepositoryNotFoundError
from pyartifactory.models import AnyRepository, AnyRepositoryResponse
from pyartifactory.models.repository import (
    LocalRepository,
    LocalRepositoryResponse,
    RemoteRepository,
    RemoteRepositoryResponse,
    SimpleRepository,
    VirtualRepository,
    VirtualRepositoryResponse,
)
from pyartifactory.objects.object import ArtifactoryObject
from pyartifactory.utils import custom_encoder

logger = logging.getLogger("pyartifactory")


class ArtifactoryRepository(ArtifactoryObject):
    """Models an artifactory repository."""

    _uri = "repositories"

    # Repositories operations
    def get_repo(self, repo_name: str) -> AnyRepositoryResponse:
        """
        Finds repository in artifactory. Raises an exception if the repo doesn't exist.
        :param repo_name: Name of the repository to retrieve
        :return: Either a local, virtual or remote repository
        """
        try:
            response = self._get(f"api/{self._uri}/{repo_name}")
            try:
                artifact_info: AnyRepositoryResponse = LocalRepositoryResponse.model_validate(response.json())
            except ValidationError:
                try:
                    artifact_info = VirtualRepositoryResponse.model_validate(response.json())
                except ValidationError:
                    artifact_info = RemoteRepositoryResponse.model_validate(response.json())
            return artifact_info
        except requests.exceptions.HTTPError as error:
            http_response: Union[Response, None] = error.response
            if isinstance(http_response, Response) and http_response.status_code in (404, 400):
                logger.error("Repository %s does not exist", repo_name)
                raise RepositoryNotFoundError(f" Repository {repo_name} does not exist")
            raise ArtifactoryError from error

    @overload
    def create_repo(self, repo: LocalRepository) -> LocalRepositoryResponse:
        ...

    @overload
    def create_repo(self, repo: VirtualRepository) -> VirtualRepositoryResponse:
        ...

    @overload
    def create_repo(self, repo: RemoteRepository) -> RemoteRepositoryResponse:
        ...

    def create_repo(self, repo: AnyRepository) -> AnyRepositoryResponse:
        """
        Creates a local, virtual or remote repository
        :param repo: Either a local, virtual or remote repository
        :return: LocalRepositoryResponse, VirtualRepositoryResponse or RemoteRepositoryResponse object
        """
        repo_name = repo.key
        try:
            self.get_repo(repo_name)
            logger.error("Repository %s already exists", repo_name)
            raise RepositoryAlreadyExistsError(f"Repository {repo_name} already exists")
        except RepositoryNotFoundError:
            data = json.dumps(repo, default=custom_encoder)
            self._put(
                f"api/{self._uri}/{repo_name}",
                headers={"Content-Type": "application/json"},
                data=data,
            )
            logger.debug("Repository %s successfully created", repo_name)
            return self.get_repo(repo_name)

    @overload
    def update_repo(self, repo: LocalRepository) -> LocalRepositoryResponse:
        ...

    @overload
    def update_repo(self, repo: VirtualRepository) -> VirtualRepositoryResponse:
        ...

    @overload
    def update_repo(self, repo: RemoteRepository) -> RemoteRepositoryResponse:
        ...

    def update_repo(self, repo: AnyRepository) -> AnyRepositoryResponse:
        """
        Updates a local, virtual or remote repository
        :param repo: Either a local, virtual or remote repository
        :return: LocalRepositoryResponse, VirtualRepositoryResponse or RemoteRepositoryResponse object
        """
        repo_name = repo.key
        self.get_repo(repo_name)

        repo_dict = json.dumps(repo.model_dump(exclude_unset=True), default=custom_encoder)

        self._post(
            f"api/{self._uri}/{repo_name}",
            headers={"Content-Type": "application/json"},
            data=repo_dict,
        )
        logger.debug("Repository %s successfully updated", repo_name)
        return self.get_repo(repo_name)

    # Remote repositories operations
    def list(self) -> List[SimpleRepository]:
        """
        Lists all the repositories
        :return: A list of repositories
        """
        response = self._get(f"api/{self._uri}")
        logger.debug("List all repositories successful")
        return [SimpleRepository(**repository) for repository in response.json()]

    def delete(self, repo_name: str) -> None:
        """
        Removes a local repository
        :param repo_name: Name of the repository to delete
        :return: None
        """

        self._delete(f"api/{self._uri}/{repo_name}")
        logger.debug("Repository %s successfully deleted", repo_name)
