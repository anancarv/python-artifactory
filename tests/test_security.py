import responses
import pytest

from pyartifactory import ArtifactorySecurity
from pyartifactory.models import AuthModel, PasswordModel, ApiKeyModel
from pyartifactory.exception import InvalidTokenDataException


URL = "http://localhost:8080/artifactory"
AUTH = ("user", "password_or_apiKey")
PASSWORD = PasswordModel(password="test_password")
API_KEY = ApiKeyModel(apiKey="test_api_key")


@responses.activate
def test_get_encrypted_password():
    data = PASSWORD.dict()
    data["password"] = PASSWORD.password.get_secret_value()
    responses.add(
        responses.GET, f"{URL}/api/security/encryptedPassword", json=data, status=200
    )

    artifactory_security = ArtifactorySecurity(AuthModel(url=URL, auth=AUTH))
    enc_pass = artifactory_security.get_encrypted_password()
    assert enc_pass.password.get_secret_value() == PASSWORD.password.get_secret_value()


@responses.activate
def test_create_api_key():
    data = API_KEY.dict()
    data["apiKey"] = API_KEY.apiKey.get_secret_value()
    responses.add(responses.POST, f"{URL}/api/security/apiKey", json=data, status=200)

    artifactory_security = ArtifactorySecurity(AuthModel(url=URL, auth=AUTH))
    api_key = artifactory_security.create_api_key()
    assert api_key.apiKey.get_secret_value() == API_KEY.apiKey.get_secret_value()


@responses.activate
def test_regenerate_api_key():
    data = API_KEY.dict()
    data["apiKey"] = API_KEY.apiKey.get_secret_value()
    responses.add(responses.PUT, f"{URL}/api/security/apiKey", json=data, status=200)

    artifactory_security = ArtifactorySecurity(AuthModel(url=URL, auth=AUTH))
    api_key = artifactory_security.regenerate_api_key()
    assert api_key.apiKey.get_secret_value() == API_KEY.apiKey.get_secret_value()


@responses.activate
def test_get_api_key():
    data = API_KEY.dict()
    data["apiKey"] = API_KEY.apiKey.get_secret_value()
    responses.add(responses.GET, f"{URL}/api/security/apiKey", json=data, status=200)

    artifactory_security = ArtifactorySecurity(AuthModel(url=URL, auth=AUTH))
    api_key = artifactory_security.get_api_key()
    assert api_key.apiKey.get_secret_value() == API_KEY.apiKey.get_secret_value()


@responses.activate
def test_revoke_api_key():
    responses.add(responses.DELETE, f"{URL}/api/security/apiKey", status=200)

    artifactory_security = ArtifactorySecurity(AuthModel(url=URL, auth=AUTH))
    artifactory_security.revoke_api_key()


@responses.activate
def test_revoke_user_api_key():
    responses.add(responses.DELETE, f"{URL}/api/security/apiKey/test_user", status=200)

    artifactory_security = ArtifactorySecurity(AuthModel(url=URL, auth=AUTH))
    artifactory_security.revoke_user_api_key("test_user")


@responses.activate
def test_create_access_token():
    responses.add(
        responses.POST,
        f"{URL}/api/security/token",
        status=200,
        json={
            "access_token": "<the access token>",
            "expires_in": 3600,
            "scope": "api:* member-of-groups:g1, g2",
            "token_type": "Bearer",
            "refresh_token": False,
        },
    )

    artifactory_security = ArtifactorySecurity(AuthModel(url=URL, auth=AUTH))
    access_token = artifactory_security.create_access_token(
        user_name="my-username", expires_in=3600, refreshable=False, groups=["g1", "g2"]
    )
    assert access_token.refresh_token is False
    assert access_token.scope == "api:* member-of-groups:g1, g2"


@responses.activate
def test_revoke_access_token_success():
    responses.add(responses.POST, f"{URL}/api/security/token/revoke", status=200)

    artifactory_security = ArtifactorySecurity(AuthModel(url=URL, auth=AUTH))
    result = artifactory_security.revoke_access_token(token="my-token")
    assert result is True


@responses.activate
def test_revoke_access_token_fail_no_token_provided():
    responses.add(responses.POST, f"{URL}/api/security/token/revoke", status=400)

    artifactory_security = ArtifactorySecurity(AuthModel(url=URL, auth=AUTH))
    with pytest.raises(InvalidTokenDataException):
        result = artifactory_security.revoke_access_token()
        assert result is False
