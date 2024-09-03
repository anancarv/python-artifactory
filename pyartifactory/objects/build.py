from __future__ import annotations

import logging
from typing import List, Optional, Union

import pydantic_core
import requests
from requests import Response

from pyartifactory.exception import ArtifactoryBuildError, ArtifactoryError, BuildNotFoundError
from pyartifactory.models.build import (
    BuildCreateRequest,
    BuildDeleteRequest,
    BuildDiffResponse,
    BuildError,
    BuildInfo,
    BuildListResponse,
    BuildPromotionRequest,
    BuildPromotionResult,
)
from pyartifactory.objects.object import ArtifactoryObject

logger = logging.getLogger("pyartifactory")


class ArtifactoryBuild(ArtifactoryObject):
    """Models an artifactory build."""

    _uri = "build"

    def get_build_info(self, build_name: str, build_number: str, properties: Optional[List[str]] = None) -> BuildInfo:
        """
        :param build_name: Build name to be retrieved
        :param build_number: Build number to be retrieved
        :param properties: List of strings like ["started=...", "diff=..."] , for admitted values
                           see https://jfrog.com/help/r/jfrog-rest-apis/build-info
        :return: BuildInfo model object containing server response
        """
        build_name = build_name.lstrip("/")
        build_number = build_number.lstrip("/")
        _query_string = ""
        if properties:
            _query_string = "?" + "&".join(properties)

        try:
            response = self._get(
                f"api/{self._uri}/{build_name}/{build_number}{_query_string}",
            )
            self._response_checker(response)
            logger.debug("Build Info successfully retrieved")
            return BuildInfo(**response.json())
        except requests.exceptions.HTTPError as error:
            http_response: Union[Response, None] = error.response
            if isinstance(http_response, Response) and http_response.status_code == 404:
                raise BuildNotFoundError(f"Build {build_number} were not found on {build_name}")
            raise ArtifactoryError from error
        except ArtifactoryBuildError as error:
            if error.status == 404:
                raise BuildNotFoundError(error.message)
            raise ArtifactoryError from error

    def create_build(self, create_build_request: BuildCreateRequest):
        try:
            _existing_build_info = self.get_build_info(create_build_request.name, create_build_request.number)
        except BuildNotFoundError:
            _resp = self._put(f"api/{self._uri}", json=create_build_request.model_dump())
            if _resp.status_code != 204:
                logger.error("Build %s in %s not created", create_build_request.number, create_build_request.name)
                raise ArtifactoryError(
                    f"Build {create_build_request.number} in {create_build_request.name} not created",
                )
            logging.debug("Build %s in %s successfully created", create_build_request.number, create_build_request.name)
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
            response = self._get(
                f"api/{self._uri}/{build_name}/{build_number}",
            )
            self._response_checker(response)
        except requests.exceptions.HTTPError as error:
            http_response: Union[Response, None] = error.response
            if isinstance(http_response, Response) and http_response.status_code == 404:
                raise BuildNotFoundError(f"Build {build_number} were not found on {build_name}")
            raise ArtifactoryError from error
        except ArtifactoryBuildError as error:
            if error.status == 404:
                raise BuildNotFoundError(error.message)
            raise ArtifactoryError from error
        else:
            response = self._post(
                f"api/{self._uri}/promote/{build_name}/{build_number}",
                json=promotion_request.model_dump(),
            )
            promotion_result = BuildPromotionResult(**response.json())
            return promotion_result

    def list(self) -> BuildListResponse:
        """
        :return: BuildListResponse model object containing server response
        """
        response = self._get(f"api/{self._uri}")
        logger.debug("List all builds successful")
        build_list: BuildListResponse = BuildListResponse.model_validate(response.json())
        return build_list

    def delete(self, delete_build: BuildDeleteRequest) -> None:
        """
        :param delete_build: Model object containing required parameters
        :return: None
        """
        try:
            for _build_number in delete_build.buildNumbers:
                response = self._get(
                    f"api/{self._uri}/{delete_build.buildName}/{_build_number}",
                )
                self._response_checker(response)
        except requests.exceptions.HTTPError as error:
            http_response: Union[Response, None] = error.response
            if isinstance(http_response, Response) and http_response.status_code == 404:
                _http_error = BuildError(**http_response.json())
                raise BuildNotFoundError("\n".join([_error.message for _error in _http_error.errors]))
            raise ArtifactoryError from error
        except ArtifactoryBuildError as error:
            if error.status == 404:
                raise BuildNotFoundError(error.message)
            # at least one build number does not exist
            raise ArtifactoryError from error
        else:
            # all build numbers exist
            _del = self._post(f"api/{self._uri}/delete", json=delete_build.model_dump())
            logger.debug(_del.text)

    def build_rename(self, build_name: str, new_build_name: str) -> None:
        """
        :param build_name: Build to be renamed
        :param new_build_name: New Build name
        :return: None
        """
        try:
            response = self._get(
                f"api/{self._uri}/{build_name}",
            )
            self._response_checker(response)
        except requests.exceptions.HTTPError as error:
            http_response: Union[Response, None] = error.response
            if isinstance(http_response, Response) and http_response.status_code == 404:
                raise BuildNotFoundError(f"Build {build_name} were not found")
            raise ArtifactoryError from error
        except ArtifactoryBuildError as error:
            raise ArtifactoryError from error
        else:
            self._post(f"api/{self._uri}/rename/{build_name}?to={new_build_name}")
            logger.debug("Build %s successfully renamed to %s", build_name, new_build_name)

    def build_diff(self, build_name: str, build_number: str, older_build_number: str) -> BuildDiffResponse:
        """
        :param build_name: Build name to be compared
        :param build_number: More recent build to be compared
        :param older_build_number: Starting build to be compared
        :return: BuildDiffResponse model object containing server response
        """
        build_name = build_name.lstrip("/")
        build_number = build_number.lstrip("/")
        older_build_number = older_build_number.lstrip("/")
        # self._check_build_number_value(build_number)
        # self._check_build_number_value(older_build_number)

        try:
            response = self._get(
                f"api/{self._uri}/{build_name}/{build_number}?diff={older_build_number}",
            )
            self._response_checker(response)
            logger.debug("Build Diff successfully retrieved")
            return BuildDiffResponse(**response.json())
        except requests.exceptions.HTTPError as error:
            http_response: Union[Response, None] = error.response
            if isinstance(http_response, Response) and http_response.status_code == 404:
                raise BuildNotFoundError(
                    f"Build diff {build_number} or {older_build_number} were not found on {build_name}",
                )
            raise ArtifactoryError from error
        except ArtifactoryBuildError as error:
            raise ArtifactoryError from error

    def _response_checker(self, response):
        try:
            _error = BuildError(**response.json())
        except pydantic_core.ValidationError:
            # response does not fit with error model
            return
        else:
            raise ArtifactoryBuildError(_error.errors[0].status, _error.errors[0].message)
