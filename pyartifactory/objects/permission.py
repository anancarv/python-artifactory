from __future__ import annotations

import logging
from typing import List, Union, overload

import requests
from requests import Response

from pyartifactory.exception import ArtifactoryError, PermissionAlreadyExistsError, PermissionNotFoundError
from pyartifactory.models import AnyPermission
from pyartifactory.models.auth import AuthModel
from pyartifactory.models.permission import Permission, PermissionV2, SimplePermission
from pyartifactory.objects.object import ArtifactoryObject

logger = logging.getLogger("pyartifactory")


class ArtifactoryPermission(ArtifactoryObject):
    """Models an artifactory permission."""

    def __init__(self, artifactory: AuthModel) -> None:
        super().__init__(artifactory)
        if self._api_version == 2:
            self._uri = "v2/security/permissions"
        if self._api_version == 1:
            self._uri = "security/permissions"

    @overload
    def create(
        self,
        permission: Permission,
    ) -> Permission:
        ...

    @overload
    def create(
        self,
        permission: PermissionV2,
    ) -> PermissionV2:
        ...

    def create(self, permission: AnyPermission) -> AnyPermission:
        """
        Creates a permission
        :param permission: Permission v2 or v1 object
        :return: Permission v2 or v1
        """
        permission_name = permission.name
        try:
            self.get(permission_name)
            logger.debug("Permission %s already exists", permission_name)
            raise PermissionAlreadyExistsError(f"Permission {permission_name} already exists")
        except PermissionNotFoundError:
            self._put(
                f"api/{self._uri}/{permission_name}",
                json=permission.model_dump(by_alias=True),
            )
            logger.debug("Permission %s successfully created", permission_name)
            return self.get(permission_name)

    def get(self, permission_name: str) -> AnyPermission:
        """
        Read permission from artifactory. Fill object if exist
        :param permission_name: Name of the permission to retrieve
        :return: Permission
        """
        try:
            response = self._get(f"api/{self._uri}/{permission_name}")
            logger.debug("Permission %s found", permission_name)
            return (
                Permission(**response.json()) if self._artifactory.api_version == 1 else PermissionV2(**response.json())
            )
        except requests.exceptions.HTTPError as error:
            http_response: Union[Response, None] = error.response
            if isinstance(http_response, Response) and http_response.status_code in (404, 400):
                logger.error("Permission %s does not exist", permission_name)
                raise PermissionNotFoundError(f"Permission {permission_name} does not exist")
            raise ArtifactoryError from error

    def list(self) -> List[SimplePermission]:
        """
        Lists all the permissions
        :return: A list of permissions
        """
        response = self._get(f"api/{self._uri}")
        logger.debug("List all permissions successful")
        return [SimplePermission(**permission) for permission in response.json()]

    @overload
    def update(self, permission: Permission) -> Permission:
        ...

    @overload
    def update(self, permission: PermissionV2) -> PermissionV2:
        ...

    def update(self, permission: AnyPermission) -> AnyPermission:
        """
        Updates an artifactory permission
        :param permission: Permission v2 or v1 object
        :return: Permission v2 or v1
        """
        permission_name = permission.name
        self._put(
            f"api/{self._uri}/{permission_name}",
            json=permission.model_dump(by_alias=True),
        )
        logger.debug("Permission %s successfully updated", permission_name)
        return self.get(permission_name)

    def delete(self, permission_name: str) -> None:
        """
        Removes an artifactory permission
        :param permission_name: Name of the permission to delete
        :return: None
        """
        self.get(permission_name)
        self._delete(f"api/{self._uri}/{permission_name}")
        logger.debug("Permission %s successfully deleted", permission_name)
