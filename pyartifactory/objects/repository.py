# Copyright (c) 2019 Ananias
# Copyright (c) 2023 Helio Chissini de Castro
#
# Licensed under the MIT license: https://opensource.org/licenses/MIT
# Permission is granted to use, copy, modify, and redistribute the work.
# Full license information available in the project LICENSE file.
#
# SPDX-License-Identifier: MIT
from __future__ import annotations

import json
import logging
import warnings
from typing import overload

import requests
from pydantic import TypeAdapter

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
            repo: AnyRepositoryResponse = TypeAdapter(AnyRepositoryResponse).validate_python(response.json())
            return repo
        except requests.exceptions.HTTPError as error:
            if error.response.status_code in (404, 400):
                logger.error("Repository %s does not exist", repo_name)
                raise RepositoryNotFoundError(f" Repository {repo_name} does not exist")
            raise ArtifactoryError from error

    @overload
    def create_repo(self, repo: LocalRepositoryResponse) -> LocalRepositoryResponse:
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

    # Local repositories operations
    def create_local_repo(self, repo: LocalRepository) -> LocalRepositoryResponse:
        """
        Creates a new local repository
        :param repo: LocalRepository object
        :return: LocalRepositoryResponse object
        """
        warnings.warn(
            "`create_local_repo()` is deprecated, use `create_repo` instead",
            DeprecationWarning,
        )
        repo_name = repo.key
        try:
            self.get_local_repo(repo_name)
            logger.error("Repository %s already exists", repo_name)
            raise RepositoryAlreadyExistsError(f"Repository {repo_name} already exists")
        except RepositoryNotFoundError:
            self._put(f"api/{self._uri}/{repo_name}", json=repo.model_dump())
            logger.debug("Repository %s successfully created", repo_name)
            return self.get_local_repo(repo_name)

    def get_local_repo(self, repo_name: str) -> LocalRepositoryResponse:
        """
        Finds repository in artifactory. Fill object if exist
        :param repo_name: Name of the repository to retrieve
        :return: LocalRepositoryResponse object
        """
        warnings.warn(
            "`get_local_repo()` is deprecated, use `get_repo` instead",
            DeprecationWarning,
        )
        try:
            response = self._get(f"api/{self._uri}/{repo_name}")
            logger.debug("Repository %s found", repo_name)
            return LocalRepositoryResponse(**response.json())
        except requests.exceptions.HTTPError as error:
            if error.response.status_code in (404, 400):
                raise RepositoryNotFoundError(f" Repository {repo_name} does not exist")
            raise ArtifactoryError from error

    def update_local_repo(self, repo: LocalRepository) -> LocalRepositoryResponse:
        """
        Updates an artifactory repository
        :param repo: LocalRepository object
        :return: LocalRepositoryResponse
        """
        warnings.warn(
            "`update_local_repo()` is deprecated, use `update_repo` instead",
            DeprecationWarning,
        )
        repo_name = repo.key
        self.get_local_repo(repo_name)
        self._post(f"api/{self._uri}/{repo_name}", json=repo.model_dump())
        logger.debug("Repository %s successfully updated", repo_name)
        return self.get_local_repo(repo_name)

    # Virtual repositories operations
    def create_virtual_repo(self, repo: VirtualRepository) -> VirtualRepositoryResponse:
        """
        Creates a new local repository
        :param repo: VirtualRepository object
        :return: VirtualRepositoryResponse object
        """
        warnings.warn(
            "`create_virtual_repo()` is deprecated, use `create_repo` instead",
            DeprecationWarning,
        )
        repo_name = repo.key
        try:
            self.get_virtual_repo(repo_name)
            logger.error("Repository %s already exists", repo_name)
            raise RepositoryAlreadyExistsError(f"Repository {repo_name} already exists")
        except RepositoryNotFoundError:
            self._put(f"api/{self._uri}/{repo_name}", json=repo.model_dump())
            logger.debug("Repository %s successfully created", repo_name)
            return self.get_virtual_repo(repo_name)

    def get_virtual_repo(self, repo_name: str) -> VirtualRepositoryResponse:
        """
        Finds repository in artifactory. Fill object if exist
        :param repo_name: Name of the repository to retrieve
        :return: VirtualRepositoryResponse object
        """
        warnings.warn(
            "`get_virtual_repo()` is deprecated, use `get_repo` instead",
            DeprecationWarning,
        )
        try:
            response = self._get(f"api/{self._uri}/{repo_name}")
            logger.debug("Repository %s found", repo_name)
            return VirtualRepositoryResponse(**response.json())
        except requests.exceptions.HTTPError as error:
            if error.response.status_code in (404, 400):
                raise RepositoryNotFoundError(f" Repository {repo_name} does not exist")
            raise ArtifactoryError from error

    def update_virtual_repo(self, repo: VirtualRepository) -> VirtualRepositoryResponse:
        """
        Updates a virtual artifactory repository
        :param repo: VirtualRepository object
        :return: VirtualRepositoryResponse
        """
        warnings.warn(
            "`update_virtual_repo()` is deprecated, use `update_repo` instead",
            DeprecationWarning,
        )
        repo_name = repo.key
        self.get_virtual_repo(repo_name)
        self._post(f"api/{self._uri}/{repo_name}", json=repo.model_dump())
        logger.debug("Repository %s successfully updated", repo_name)
        return self.get_virtual_repo(repo_name)

    # Remote repositories operations
    def create_remote_repo(self, repo: RemoteRepository) -> RemoteRepositoryResponse:
        """
        Creates a new local repository
        :param repo: RemoteRepository object
        :return: RemoteRepositoryResponse object
        """
        warnings.warn(
            "`create_remote_repo()` is deprecated, use `create_repo` instead",
            DeprecationWarning,
        )
        repo_name = repo.key
        try:
            self.get_remote_repo(repo_name)
            logger.error("Repository %s already exists", repo_name)
            raise RepositoryAlreadyExistsError(f"Repository {repo_name} already exists")
        except RepositoryNotFoundError:
            self._put(f"api/{self._uri}/{repo_name}", json=repo.model_dump())
            logger.debug("Repository %s successfully created", repo_name)
            return self.get_remote_repo(repo_name)

    def get_remote_repo(self, repo_name: str) -> RemoteRepositoryResponse:
        """
        Finds a remote repository in artifactory. Fill object if exist
        :param repo_name: Name of the repository to retrieve
        :return: RemoteRepositoryResponse object
        """
        warnings.warn(
            "`get_remote_repo()` is deprecated, use `get_repo` instead",
            DeprecationWarning,
        )
        try:
            response = self._get(f"api/{self._uri}/{repo_name}")
            logger.debug("Repository %s found", repo_name)
            return RemoteRepositoryResponse(**response.json())
        except requests.exceptions.HTTPError as error:
            if error.response.status_code in (404, 400):
                raise RepositoryNotFoundError(f" Repository {repo_name} does not exist")
            raise ArtifactoryError from error

    def update_remote_repo(self, repo: RemoteRepository) -> RemoteRepositoryResponse:
        """
        Updates a remote artifactory repository
        :param repo: VirtualRepository object
        :return: VirtualRepositoryResponse
        """
        warnings.warn(
            "`update_remote_repo()` is deprecated, use `update_repo` instead",
            DeprecationWarning,
        )
        repo_name = repo.key
        self.get_remote_repo(repo_name)
        self._post(f"api/{self._uri}/{repo_name}", json=repo.model_dump())
        logger.debug("Repository %s successfully updated", repo_name)
        return self.get_remote_repo(repo_name)

    def list_all(self) -> list[SimpleRepository]:
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
