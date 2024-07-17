"""
Definition of artifactory base object.
"""
from __future__ import annotations

import requests
from requests import Response

from pyartifactory.models import AuthModel


class ArtifactoryObject:
    """Models the artifactory object."""

    def __init__(self, artifactory: AuthModel) -> None:
        self._artifactory = artifactory
        self._auth = (
            self._artifactory.auth[0],
            self._artifactory.auth[1].get_secret_value(),
        )
        self._api_version = self._artifactory.api_version
        self._verify = self._artifactory.verify
        self._cert = self._artifactory.cert
        self._timeout = self._artifactory.timeout
        self.session = requests.Session()

    def _get(self, route: str, **kwargs) -> Response:
        """
        :param route: API Route
        :param kwargs: Additional parameters to add the request
        :returns  An HTTP response
        """
        return self._generic_http_method_request("get", route, **kwargs)

    def _post(self, route: str, **kwargs) -> Response:
        """
        :param route: API Route
        :param kwargs: Additional parameters to add the request
        :returns  An HTTP response
        """
        return self._generic_http_method_request("post", route, **kwargs)

    def _put(self, route: str, **kwargs) -> Response:
        """
        :param route: API Route
        :param kwargs: Additional parameters to add the request
        :returns  An HTTP response
        """
        return self._generic_http_method_request("put", route, **kwargs)

    def _delete(self, route: str, **kwargs) -> Response:
        """
        :param route: API Route
        :param kwargs: Additional parameters to add the request
        :returns  An HTTP response
        """
        return self._generic_http_method_request("delete", route, **kwargs)

    def _patch(self, route: str, **kwargs) -> Response:
        """
        :param route: API Route
        :param kwargs: Additional parameters to add the request
        :returns  An HTTP response
        """
        return self._generic_http_method_request("patch", route, **kwargs)

    def _generic_http_method_request(
        self,
        method: str,
        route: str,
        raise_for_status: bool = True,
        **kwargs,
    ) -> Response:
        """
        :param method: HTTP method to use
        :param route: API Route
        :param kwargs: Additional parameters to add the request
        :return: An HTTP response
        """

        http_method = getattr(self.session, method)
        response: Response = http_method(
            f"{self._artifactory.url}/{route}",
            auth=self._auth,
            **kwargs,
            verify=self._verify,
            cert=self._cert,
            timeout=self._timeout,
        )
        if raise_for_status:
            response.raise_for_status()
        return response
