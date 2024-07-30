from __future__ import annotations

import logging
import os
import urllib
from collections.abc import Iterator
from pathlib import Path
from typing import Dict, List, Optional, Union

import requests
from pydantic import ValidationError
from requests import Response

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
            artifact_path = Path(artifact_path.lstrip("/"))

        try:
            artifact_as_posix = artifact_path.as_posix()
            artifact_as_url = urllib.parse.quote(artifact_as_posix)
            response = self._get(f"api/storage/{artifact_as_url}")
            try:
                artifact_info: ArtifactInfoResponse = ArtifactFolderInfoResponse.model_validate(response.json())
            except ValidationError:
                artifact_info = ArtifactFileInfoResponse.model_validate(response.json())
            return artifact_info
        except requests.exceptions.HTTPError as error:
            http_response: Union[Response, None] = error.response
            if isinstance(http_response, Response) and http_response.status_code == 404:
                logger.error("Artifact %s does not exist", artifact_path)
                raise ArtifactNotFoundError(f"Artifact {artifact_path} does not exist")
            raise ArtifactoryError from error

    def deploy(self, local_file_location: Union[Path, str], artifact_path: Union[Path, str]) -> ArtifactInfoResponse:
        """
        Deploy a file or directory.
        :param artifact_path: Path to artifactory in Artifactory
        :param local_file_location: Location of the file or folder to deploy
        """
        local_file = Path(local_file_location)
        artifact_folder = Path(artifact_path)

        if local_file.is_dir():
            for root, _, files in os.walk(local_file.as_posix()):
                new_root = f"{artifact_folder}/{root[len(local_file.as_posix()):]}"
                for file in files:
                    self.deploy(Path(f"{root}/{file}"), Path(f"{new_root}/{file}"))
        else:
            with local_file.open(mode="rb") as streamfile:
                self._put(route=artifact_folder.as_posix(), data=streamfile)
                logger.debug("Artifact %s successfully deployed", artifact_folder.name)
        return self.info(artifact_folder)

    @staticmethod
    def _get_path_prefix(artifact_path: str):
        if artifact_path.startswith("/"):
            artifact_path = artifact_path[1:]
        return artifact_path.rsplit("/", 1)[0] + "/" if "/" in artifact_path else ""

    @staticmethod
    def _remove_prefix(_str: str, prefix: str) -> str:
        if _str.startswith(prefix):
            return _str[len(prefix) :]
        raise ValueError(f"Input string, '{_str}', doesn't have the prefix: '{prefix}'")

    def _download(self, artifact_path: str, local_directory_path: Optional[Path] = None) -> Path:
        """
        Download artifact (file) into local directory.
        :param artifact_path: Path to file in Artifactory
        :param local_directory_path: Local path to where the artifact will be downloaded
        :return: File name
        """
        artifact_path = artifact_path.lstrip("/")
        local_filename = artifact_path.split("/")[-1]

        if local_directory_path:
            local_directory_path.mkdir(parents=True, exist_ok=True)
            local_file_full_path = local_directory_path / local_filename
        else:
            local_file_full_path = Path(local_filename)

        artifact_path_url = urllib.parse.quote(artifact_path)
        with self._get(f"{artifact_path_url}", stream=True) as response, local_file_full_path.open("wb") as file:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:  # filter out keep-alive new chunks
                    file.write(chunk)
        logger.debug("Artifact %s successfully downloaded", local_filename)
        return local_file_full_path

    def download(self, artifact_path: str, local_directory_path: str = ".") -> Path:
        """
        Download artifact (file or directory) into local directory.
        :param artifact_path: Path to file or directory in Artifactory
        :param local_directory_path: Local path to where the artifact will be downloaded
        :return: File name
        """
        artifact_path = artifact_path.rstrip("/")
        basename = artifact_path.split("/")[-1]
        prefix = self._get_path_prefix(artifact_path)
        for art in self._walk(artifact_path):
            full_path = art.repo + art.path
            local_artifact_path = self._remove_prefix(full_path, prefix)
            local_path = Path(local_directory_path) / local_artifact_path
            if isinstance(art, ArtifactFolderInfoResponse):
                local_path.mkdir(exist_ok=True)
            else:
                self._download(full_path, local_path.parent)
        return Path(local_directory_path).joinpath(basename)

    def list(
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
            artifact_list: ArtifactListResponse = ArtifactListResponse.model_validate(response.json())
            return artifact_list
        except requests.exceptions.HTTPError as error:
            http_response: Union[Response, None] = error.response
            if isinstance(http_response, Response) and http_response.status_code == 404:
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
            http_response: Union[Response, None] = error.response
            if isinstance(http_response, Response) and http_response.status_code == 404:
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
            http_response: Union[Response, None] = error.response
            if isinstance(http_response, Response) and http_response.status_code == 404:
                logger.error("Artifact %s does not exist", artifact_path)
                raise ArtifactNotFoundError(f"Artifact {artifact_path} does not exist")
            if isinstance(http_response, Response) and http_response.status_code == 400:
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
                params={"recursiveProperties": int(recursive)},
                headers={"Content-Type": "application/json"},
                json={"props": properties},
            )
            logger.debug("Artifact Properties successfully updated")
            return self.properties(artifact_path)
        except requests.exceptions.HTTPError as error:
            http_response: Union[Response, None] = error.response
            if isinstance(http_response, Response) and http_response.status_code == 400:
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
