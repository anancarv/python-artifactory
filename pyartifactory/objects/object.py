"""
Definition of artifactory base object.
"""

from __future__ import annotations

from typing import Optional, Tuple

import requests
from requests import Response

from pyartifactory.models import AuthModel
from pyartifactory.utils import remove_suffix


class ArtifactoryObject:
    """Models the artifactory object."""

    def __init__(self, artifactory: AuthModel) -> None:
        self._artifactory = artifactory
        self._auth: Optional[Tuple[str, str]] = None

        if self._artifactory.auth is not None:
            self._auth = (
                self._artifactory.auth[0],
                self._artifactory.auth[1].get_secret_value(),
            )

        self._access_token = self._artifactory.access_token
        self._api_version = self._artifactory.api_version
        self._verify = self._artifactory.verify
        self._cert = self._artifactory.cert
        self._timeout = self._artifactory.timeout
        self.session = requests.Session()

    def _get(self, route: str, art_service: str = "artifactory", **kwargs) -> Response:
        """
        :param route: API Route
        :param kwargs: Additional parameters to add the request
        :returns  An HTTP response
        """
        return self._generic_http_method_request("get", route, art_service, **kwargs)

    def _post(self, route: str, art_service: str = "artifactory", **kwargs) -> Response:
        """
        :param route: API Route
        :param kwargs: Additional parameters to add the request
        :returns  An HTTP response
        """
        return self._generic_http_method_request("post", route, art_service, **kwargs)

    def _put(self, route: str, art_service: str = "artifactory", **kwargs) -> Response:
        """
        :param route: API Route
        :param kwargs: Additional parameters to add the request
        :returns  An HTTP response
        """
        return self._generic_http_method_request("put", route, art_service, **kwargs)

    def _delete(self, route: str, art_service: str = "artifactory", **kwargs) -> Response:
        """
        :param route: API Route
        :param kwargs: Additional parameters to add the request
        :returns  An HTTP response
        """
        return self._generic_http_method_request("delete", route, art_service, **kwargs)

    def _patch(self, route: str, art_service: str = "artifactory", **kwargs) -> Response:
        """
        :param route: API Route
        :param kwargs: Additional parameters to add the request
        :returns  An HTTP response
        """
        return self._generic_http_method_request("patch", route, art_service, **kwargs)

    def _generic_http_method_request(
        self,
        method: str,
        route: str,
        art_service: str = "artifactory",
        raise_for_status: bool = True,
        **kwargs,
    ) -> Response:
        """
        :param method: HTTP method to use
        :param route: API Route
        :param kwargs: Additional parameters to add the request
        :return: An HTTP response
        """

        if self._access_token is not None:
            headers = kwargs.get("headers", {})
            headers["Authorization"] = f"Bearer {self._access_token}"
            kwargs["headers"] = headers

            auth = None
        else:
            auth = self._auth

        http_method = getattr(self.session, method)
        uri = remove_suffix(
            self._artifactory.url,
            "/artifactory",
        )  # to support base urls with or without /artifactory suffix
        response: Response = http_method(
            f"{uri}/{art_service}/{route}",
            auth=auth,
            **kwargs,
            verify=self._verify,
            cert=self._cert,
            timeout=self._timeout,
        )
        if raise_for_status:
            response.raise_for_status()
        return response
