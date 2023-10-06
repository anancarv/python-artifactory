from __future__ import annotations

import logging
import os
import typing
from collections.abc import Iterator
from pathlib import Path
from typing import Dict, List, Optional, Union

import requests
from pydantic import TypeAdapter

from pyartifactory.exception import ArtifactNotFoundError, ArtifactoryError, BadPropertiesError, PropertyNotFoundError
from pyartifactory.models.artifact import (
    ArtifactFileInfoResponse,
    ArtifactFolderInfoResponse,
    ArtifactInfoResponse,
    ArtifactListResponse,
    ArtifactPropertiesResponse,
    ArtifactStatsResponse,
)
from pyartifactory.objects.object import ArtifactoryObject

logger = logging.getLogger("pyartifactory")


class ArtifactoryArtifact(ArtifactoryObject):
    """Models an artifactory artifact."""

    def _walk(self, artifact_path: str, topdown: bool = True) -> Iterator[ArtifactInfoResponse]:
        """Iterate over artifact (file or directory) recursively.

        :param artifact_path: Path to file or folder in Artifactory
        :param topdown: True for a top-down (directory first) traversal
        """
        info = self.info(artifact_path)
        if not isinstance(info, ArtifactFolderInfoResponse):
            yield info
        else:
            if topdown:
                yield info
            for subdir in (child for child in info.children if child.folder is True):
                yield from self._walk(artifact_path + subdir.uri, topdown=topdown)
            for file in (child for child in info.children if child.folder is not True):
                yield from self._walk(artifact_path + file.uri, topdown=topdown)
            if not topdown:
                yield info

    def info(self, artifact_path: Union[Path, str]) -> ArtifactInfoResponse:
        """
        Retrieve information about a file or a folder

        See https://www.jfrog.com/confluence/display/JFROG/Artifactory+REST+API#ArtifactoryRESTAPI-FolderInfo
        and https://www.jfrog.com/confluence/display/JFROG/Artifactory+REST+API#ArtifactoryRESTAPI-FileInfo

        :param artifact_path: Path to file or folder in Artifactory
        """

        if isinstance(artifact_path, str):
            artifact_path = Path(artifact_path)

        try:
            response = self._get(f"api/storage/{artifact_path.as_posix()}")
            model = TypeAdapter(ArtifactInfoResponse).validate_python(response.json())
            return typing.cast(ArtifactInfoResponse, model)
        except requests.exceptions.HTTPError as error:
            if error.response.status_code == 404:
                logger.error("Artifact %s does not exist", artifact_path)
                raise ArtifactNotFoundError(f"Artifact {artifact_path} does not exist")
            raise ArtifactoryError from error

    def deploy(self, local_file_location: Path, artifact_path: Path) -> ArtifactInfoResponse:
        """
        Deploy a file or directory.
        :param artifact_path: Path to artifactory in Artifactory
        :param local_file_location: Location of the file or folder to deploy
        """

        if local_file_location.is_dir():
            for root, _, files in os.walk(local_file_location.as_posix()):
                new_root = f"{artifact_path}/{root[len(local_file_location.as_posix()):]}"
                for file in files:
                    self.deploy(Path(f"{root}/{file}"), Path(f"{new_root}/{file}"))
        else:
            with local_file_location.open(mode="rb") as streamfile:
                self._put(route=artifact_path.as_posix(), data=streamfile)
                logger.debug("Artifact %s successfully deployed", artifact_path.name)
        return self.info(artifact_path)

    def _download(self, artifact_path: Path, local_directory_path: Path, flat: bool = False):
        """
        Download artifact (file) into local directory.
        :param artifact_path: Path to file in Artifactory
        :param local_directory_path: Local path to where the artifact will be downloaded
        :return: File name
        """

        info = self.info(artifact_path)
        target_path = Path(info.repo) / Path(info.path[1:])

        if isinstance(info, ArtifactFolderInfoResponse):
            if not flat:
                local_directory_path.joinpath(target_path).mkdir(parents=True, exist_ok=True)
            for child in info.children:
                self._download(target_path.joinpath(child.uri[1:]), local_directory_path)
        elif isinstance(info, ArtifactFileInfoResponse):
            file_path = (
                local_directory_path.joinpath(target_path)
                if not flat
                else local_directory_path.joinpath(target_path.name)
            )
            if not flat:
                local_directory_path.joinpath(target_path).parent.mkdir(parents=True, exist_ok=True)
            with self._get(artifact_path.as_posix(), stream=True) as response, file_path.open(
                mode="wb",
            ) as file:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:  # filter out keep-alive new chunks
                        file.write(chunk)
                logger.debug(
                    "Artifact %s successfully downloaded",
                    target_path.as_posix(),
                )

    def download(
        self,
        artifact_path: Union[Path, str],
        local_directory_path: Union[Path, str] = Path().cwd(),
        flat: bool = False,
    ) -> Optional[Path]:
        """
        Download artifact (file or directory) into local directory.
        :param artifact_path: Path to file or directory in Artifactory
        :param local_directory_path: Local path to where the artifact will be downloaded
        :param flat: If set to true, the files will be downloaded to the same directory without the folder structure
        :return: Path object
        """
        if isinstance(artifact_path, str):
            artifact_path = Path(artifact_path)
        if isinstance(local_directory_path, str):
            local_directory_path = Path(local_directory_path)

        # Strip left slash and remove first path entry mimicking
        # Jfrog repository path structure
        path_str = artifact_path.as_posix().lstrip("/")
        try:
            self._download(Path(path_str), local_directory_path, flat=flat)
            return local_directory_path.joinpath(artifact_path.name)
        except ArtifactNotFoundError:
            logger.error("Artifact %s does not exist", artifact_path)
        return None

    def file_list(
        self,
        artifact_path: str,
        recursive: bool = True,
        depth: Optional[int] = None,
        list_folders: bool = True,
    ) -> ArtifactListResponse:
        """
        Retrieve a list of files or a folders

        See https://www.jfrog.com/confluence/display/JFROG/Artifactory+REST+API#ArtifactoryRESTAPI-FileList

        :param artifact_path: Path to folder in Artifactory
        :param recursive: Recursively retrieve files and folders
        :param depth: The depth to recursively retrieve
        :param list_folders: Whether or not to include folders in the response
        :return: A list of artifacts in Artifactory
        """
        try:
            params = {
                "deep": int(recursive),
                "listFolders": int(list_folders),
            }
            if depth is not None:
                params.update(depth=depth)
            response = self._get(f"api/storage/{artifact_path}?list", params=params)
            artifact_list: ArtifactListResponse = TypeAdapter(ArtifactListResponse).validate_python(response.json())
            return artifact_list
        except requests.exceptions.HTTPError as error:
            if error.response.status_code == 404:
                logger.error("Artifact %s does not exist", artifact_path)
                raise ArtifactNotFoundError(f"Artifact {artifact_path} does not exist")
            raise ArtifactoryError from error

    def properties(self, artifact_path: str, properties: Optional[List[str]] = None) -> ArtifactPropertiesResponse:
        """
        :param artifact_path: Path to file in Artifactory
        :param properties: List of properties to retrieve
        :return: Artifact properties
        """
        if properties is None:
            properties = []
        artifact_path = artifact_path.lstrip("/")
        try:
            response = self._get(
                f"api/storage/{artifact_path}",
                params={"properties": ",".join(properties)},
            )
            logger.debug("Artifact Properties successfully retrieved")
            return ArtifactPropertiesResponse(**response.json())
        except requests.exceptions.HTTPError as error:
            if error.response.status_code == 404:
                raise PropertyNotFoundError(f"Properties {properties} were not found on artifact {artifact_path}")
            raise ArtifactoryError from error

    def set_properties(
        self,
        artifact_path: str,
        properties: Dict[str, List[str]],
        recursive: bool = True,
    ) -> ArtifactPropertiesResponse:
        """
        :param artifact_path: Path to file or folder in Artifactory
        :param properties: List of properties to update
        :param recursive: If set to true, properties will be applied recursively to subfolders and files
        :return: None
        """
        if properties is None:
            properties = {}
        artifact_path = artifact_path.lstrip("/")
        properties_param_str = ""
        for k, v in properties.items():
            values_str = ",".join(v)
            properties_param_str += f"{k}={values_str};"
        try:
            self._put(
                f"api/storage/{artifact_path}",
                params={
                    "recursive": int(recursive),
                    "properties": properties_param_str,
                },
            )
            logger.debug("Artifact Properties successfully set")
            return self.properties(artifact_path)
        except requests.exceptions.HTTPError as error:
            if error.response.status_code == 404:
                logger.error("Artifact %s does not exist", artifact_path)
                raise ArtifactNotFoundError(f"Artifact {artifact_path} does not exist")
            if error.response.status_code == 400:
                logger.error("A property value includes forbidden special characters")
                raise BadPropertiesError("A property value includes forbidden special characters")
            raise ArtifactoryError from error

    def update_properties(
        self,
        artifact_path: str,
        properties: Dict[str, List[str]],
        recursive: bool = True,
    ) -> ArtifactPropertiesResponse:
        """
        :param artifact_path: Path to file or folder in Artifactory
        :param properties: List of properties to update
        :param recursive: If set to true, properties will be applied recursively to subfolders and files
        :return: None
        """
        if properties is None:
            properties = {}
        artifact_path = artifact_path.lstrip("/")
        try:
            self._patch(
                f"api/metadata/{artifact_path}",
                params={"recursive": int(recursive)},
                headers={"Content-Type": "application/json"},
                json={"props": properties},
            )
            logger.debug("Artifact Properties successfully updated")
            return self.properties(artifact_path)
        except requests.exceptions.HTTPError as error:
            if error.response.status_code == 400:
                logger.error("Error updating artifact properties")
                raise ArtifactoryError("Error updating artifact properties")
            raise ArtifactoryError from error

    def stats(self, artifact_path: str) -> ArtifactStatsResponse:
        """
        :param artifact_path: Path to file in Artifactory
        :return: Artifact Stats
        """
        artifact_path = artifact_path.lstrip("/")
        response = self._get(f"api/storage/{artifact_path}?stats")
        logger.debug("Artifact stats successfully retrieved")
        return ArtifactStatsResponse(**response.json())

    def copy(self, artifact_current_path: str, artifact_new_path: str, dryrun: bool = False) -> ArtifactInfoResponse:
        """
        :param artifact_current_path: Current path to file
        :param artifact_new_path: New path to file
        :param dryrun: Dry run
        :return: ArtifactInfoResponse: info of the copied artifact
        """
        artifact_current_path = artifact_current_path.lstrip("/")
        artifact_new_path = artifact_new_path.lstrip("/")
        dry = 1 if dryrun else 0

        self._post(f"api/copy/{artifact_current_path}?to={artifact_new_path}&dry={dry}")
        logger.debug("Artifact %s successfully copied", artifact_current_path)
        return self.info(artifact_new_path)

    def move(self, artifact_current_path: str, artifact_new_path: str, dryrun: bool = False) -> ArtifactInfoResponse:
        """
        :param artifact_current_path: Current path to file
        :param artifact_new_path: New path to file
        :param dryrun: Dry run
        :return: ArtifactInfoResponse: info of the moved artifact
        """
        artifact_current_path = artifact_current_path.lstrip("/")
        artifact_new_path = artifact_new_path.lstrip("/")

        dry = 1 if dryrun else 0

        self._post(f"api/move/{artifact_current_path}?to={artifact_new_path}&dry={dry}")
        logger.debug("Artifact %s successfully moved", artifact_current_path)
        return self.info(artifact_new_path)

    def delete(self, artifact_path: str) -> None:
        """
        :param artifact_path: Path to file in Artifactory
        :return: bool
        """
        artifact_path = artifact_path.lstrip("/")
        self._delete(f"{artifact_path}")
        logger.debug("Artifact %s successfully deleted", artifact_path)
