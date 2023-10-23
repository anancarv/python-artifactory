from __future__ import annotations

import logging
from typing import List, Union

import requests
from requests import Response

from pyartifactory.exception import ArtifactoryError, GroupAlreadyExistsError, GroupNotFoundError
from pyartifactory.models.group import Group
from pyartifactory.objects.object import ArtifactoryObject

logger = logging.getLogger("pyartifactory")


class ArtifactoryGroup(ArtifactoryObject):
    """Models artifactory groups."""

    _uri = "security/groups"

    def create(self, group: Group) -> Group:
        """
        Creates a new group in Artifactory or replaces an existing group
        :param group: Group to create
        :return: Created group
        """
        group_name = group.name
        try:
            self.get(group_name)
            logger.error("Group %s already exists", group_name)
            raise GroupAlreadyExistsError(f"Group {group_name} already exists")
        except GroupNotFoundError:
            self._put(f"api/{self._uri}/{group_name}", json=group.model_dump())
            logger.debug("Group %s successfully created", group_name)
            return self.get(group.name)

    def get(self, name: str) -> Group:
        """
        Get the details of an Artifactory Group
        :param name: Name of the group to retrieve
        :return: Found artifactory group
        """
        try:
            response = self._get(f"api/{self._uri}/{name}", params={"includeUsers": True})
            logger.debug("Group %s found", name)
            return Group(**response.json())
        except requests.exceptions.HTTPError as error:
            http_response: Union[Response, None] = error.response
            if isinstance(http_response, Response) and http_response.status_code in (404, 400):
                logger.error("Group %s does not exist", name)
                raise GroupNotFoundError(f"Group {name} does not exist")
            raise ArtifactoryError from error

    def list(self) -> List[Group]:
        """
        Lists all the groups
        :return: GroupList
        """
        response = self._get(f"api/{self._uri}")
        logger.debug("List all groups successful")
        return [Group(**group) for group in response.json()]

    def update(self, group: Group) -> Group:
        """
        Updates an exiting group in Artifactory with the provided group details.
        :param group: Group to be updated
        :return: Updated group
        """
        group_name = group.name
        self.get(group_name)
        self._post(f"api/{self._uri}/{group_name}", json=group.model_dump())
        logger.debug("Group %s successfully updated", group_name)
        return self.get(group_name)

    def delete(self, name: str) -> None:
        """
        Removes a group
        :param name: Name of the group to delete
        :return: None
        """
        self.get(name)
        self._delete(f"api/{self._uri}/{name}")
        logger.debug("Group %s successfully deleted", name)
