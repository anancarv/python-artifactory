from __future__ import annotations

import logging
from typing import Dict, Optional

from pyartifactory.exception import InvalidTokenDataError
from pyartifactory.models.auth import AccessTokenModel, ApiKeyModel, PasswordModel
from pyartifactory.objects.object import ArtifactoryObject

logger = logging.getLogger("pyartifactory")


class ArtifactorySecurity(ArtifactoryObject):
    """Models artifactory security."""

    _uri = "security"

    def get_encrypted_password(self) -> PasswordModel:
        """
        Get the encrypted password of the authenticated requestor.
        :return: str
        """
        response = self._get(f"api/{self._uri}/encryptedPassword")
        logger.debug("Encrypted password successfully delivered")
        return PasswordModel(**response.json())

    def create_access_token(
        self,
        user_name: str,
        expires_in: int = 3600,
        refreshable: bool = False,
        groups: Optional[str] = None,
    ) -> AccessTokenModel:
        """
        Creates an access token.

        :param user_name: Name of the user to whom an access key should be granted. transient token
                          is created if user doesn't exist in artifactory.
        :param expires_in: Expiry time for the token in seconds. For eternal tokens specify 0.
        :param refreshable: If set to true token can be refreshed using the refresh token returned.
        :param groups: A list of groups the token has membership of.
                       If an existing user in artifactory is used with existing memberships
                       groups are automatically implied without specification.
        :return: AccessToken
        """
        payload = {
            "username": user_name,
            "expires_in": expires_in,
            "refreshable": refreshable,
        }
        if groups:
            if not isinstance(groups, list):
                raise ValueError(groups)
            scope = f'member-of-groups:"{",".join(groups)}"'
            payload.update({"scope": scope})
        response = self._post(f"api/{self._uri}/token", data=payload, raise_for_status=False)
        if response.ok:
            return AccessTokenModel(**response.json())
        raise InvalidTokenDataError(response.json().get("error_description", "Unknown error"))

    def revoke_access_token(self, token: Optional[str] = None, token_id: Optional[str] = None) -> bool:
        """
        Revokes an access token.

        :param token: The token to revoke
        :param token_id: The id of a token to revoke
        :return: bool True or False indicating success or failure of token revocation attempt.
        """
        if not any([token, token_id]):
            logger.error("Neither a token or a token id was specified")
            raise InvalidTokenDataError
        payload: Dict[str, Optional[str]] = {"token": token} if token else {"token_id": token_id}
        response = self._post(f"api/{self._uri}/token/revoke", data=payload, raise_for_status=False)
        if response.ok:
            logger.debug("Token revoked successfully, or token did not exist")
            return True
        logger.error("Token revocation unsuccessful, response was %s", response.text)
        return False

    def create_api_key(self) -> ApiKeyModel:
        """
        Create an API key for the current user.
        :return: Error if API key already exists - use regenerate API key instead.
        """
        response = self._post(f"api/{self._uri}/apiKey")
        logger.debug("API Key successfully created")
        return ApiKeyModel(**response.json())

    def regenerate_api_key(self) -> ApiKeyModel:
        """
        Regenerate an API key for the current user
        :return: API key
        """
        response = self._put(f"api/{self._uri}/apiKey")
        logger.debug("API Key successfully regenerated")
        return ApiKeyModel(**response.json())

    def get_api_key(self) -> ApiKeyModel:
        """
        Get the current user's own API key
        :return: API key
        """
        response = self._get(f"api/{self._uri}/apiKey")
        logger.debug("API Key successfully delivered")
        return ApiKeyModel(**response.json())

    def revoke_api_key(self) -> None:
        """
        Revokes the current user's API key
        :return: None
        """
        self._delete(f"api/{self._uri}/apiKey")
        logger.debug("API Key successfully revoked")

    def revoke_user_api_key(self, name: str) -> None:
        """
        Revokes the API key of another user
        :param name: name of the user to whom api key has to be revoked
        :return: None
        """
        self._delete(f"api/{self._uri}/apiKey/{name}")
        logger.debug("User API Key successfully revoked")
