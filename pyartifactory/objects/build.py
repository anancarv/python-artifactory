from __future__ import annotations

import logging
from typing import Union

import requests
from requests import Response

from pyartifactory.exception import ArtifactoryError, BuildNotFoundError
from pyartifactory.models.build import (
    BuildCreateRequest,
    BuildDeleteRequest,
    BuildDiffResponse,
    BuildError,
    BuildInfo,
    BuildListResponse,
    BuildPromotionRequest,
    BuildPromotionResult,
    BuildProperties,
)
from pyartifactory.objects.object import ArtifactoryObject

logger = logging.getLogger("pyartifactory")


class ArtifactoryBuild(ArtifactoryObject):
    """Models an artifactory build."""

    _uri = "build"

    def get_build_info(
        self,
        build_name: str,
        build_number: str,
        properties: BuildProperties = BuildProperties(),
    ) -> BuildInfo:
        """
        :param build_name: Build name to be retrieved
        :param build_number: Build number to be retrieved
        :param properties: Build properties model, for admitted values
                           see https://jfrog.com/help/r/jfrog-rest-apis/build-info
        :return: BuildInfo model object containing server response
        """
        try:
            response = self._get(
                f"api/{self._uri}/{build_name}/{build_number}{properties.to_query_string()}",
            )
            logger.debug("Build Info successfully retrieved")
        except requests.exceptions.HTTPError as error:
            self._raise_exception(error)

        return BuildInfo(**response.json())

    def create_build(self, create_build_request: BuildCreateRequest) -> None:
        try:
            self.get_build_info(create_build_request.name, create_build_request.number)
        except BuildNotFoundError:
            # other exception from get_build_info are forwarded to caller.
            try:
                # build does not exist, can be created here
                self._put(f"api/{self._uri}", json=create_build_request.model_dump())
                logging.debug(
                    "Build %s in %s successfully created",
                    create_build_request.number,
                    create_build_request.name,
                )
            except requests.exceptions.HTTPError as error:
                self._raise_exception(error)
        else:
            logger.error("Build %s in %s already exists", create_build_request.number, create_build_request.name)
            raise ArtifactoryError(f"Build {create_build_request.number} in {create_build_request.name} already exists")

    def promote_build(
        self,
        build_name: str,
        build_number: str,
        promotion_request: BuildPromotionRequest,
    ) -> BuildPromotionResult:
        """
        :param build_name: Build name to be promoted
        :param build_number: Build number to be promoted
        :param promotion_request: Model object containing parameters for promotion
        :return: BuildPromotionResponse containing server response
        """
        try:
            self._get(
                f"api/{self._uri}/{build_name}/{build_number}",
            )
        except requests.exceptions.HTTPError as error:
            self._raise_exception(error)
        else:
            try:
                response = self._post(
                    f"api/{self._uri}/promote/{build_name}/{build_number}",
                    json=promotion_request.model_dump(),
                )
                logging.debug(
                    "Build %s in %s promoted from %s to %s",
                    build_number,
                    build_name,
                    promotion_request.sourceRepo,
                    promotion_request.targetRepo,
                )
            except requests.exceptions.HTTPError as error:
                self._raise_exception(error)

        return BuildPromotionResult(**response.json())

    def list(self) -> BuildListResponse:
        """
        :return: BuildListResponse model object containing server response
        """
        response = self._get(f"api/{self._uri}")
        logger.debug("List all builds successful")
        return BuildListResponse.model_validate(response.json())

    def delete(self, delete_build: BuildDeleteRequest) -> None:
        """
        :param delete_build: Model object containing required parameters
        :return: None
        """
        try:
            for _build_number in delete_build.buildNumbers:
                self._get(
                    f"api/{self._uri}/{delete_build.buildName}/{_build_number}",
                )
            # all build numbers exist
            self._post(f"api/{self._uri}/delete", json=delete_build.model_dump())
            logger.debug("Builds %s deleted from %s", ",".join(delete_build.buildNumbers), delete_build.buildName)
        except requests.exceptions.HTTPError as error:
            self._raise_exception(error)

    def build_rename(self, build_name: str, new_build_name: str) -> None:
        """
        :param build_name: Build to be renamed
        :param new_build_name: New Build name
        :return: None
        """
        try:
            self._get(
                f"api/{self._uri}/{build_name}",
            )
        except requests.exceptions.HTTPError as error:
            self._raise_exception(error)
        else:
            try:
                self._post(f"api/{self._uri}/rename/{build_name}?to={new_build_name}")
                logger.debug("Build %s successfully renamed to %s", build_name, new_build_name)
            except requests.exceptions.HTTPError as error:
                self._raise_exception(error)

    def build_diff(self, build_name: str, build_number: str, older_build_number: str) -> BuildDiffResponse:
        """
        :param build_name: Build name to be compared
        :param build_number: More recent build to be compared
        :param older_build_number: Starting build to be compared
        :return: BuildDiffResponse model object containing server response
        """
        try:
            response = self._get(
                f"api/{self._uri}/{build_name}/{build_number}?diff={older_build_number}",
            )
            logger.debug("Build Diff successfully retrieved between %s and %s", build_number, older_build_number)
        except requests.exceptions.HTTPError as error:
            self._raise_exception(error)

        return BuildDiffResponse(**response.json())

    def _raise_exception(self, error: requests.exceptions.HTTPError):
        http_response: Union[Response, None] = error.response
        if isinstance(http_response, Response):
            _http_error = BuildError(**http_response.json())
            if http_response.status_code == 404:
                raise BuildNotFoundError(_http_error.to_error_message()) from error
            raise ArtifactoryError(_http_error.to_error_message()) from error
        else:
            raise ArtifactoryError from error
