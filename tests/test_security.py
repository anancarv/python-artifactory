import responses

from pyartifactory import ArtfictorySecurity
from pyartifactory.models.Auth import AuthModel, PasswordModel, ApiKeyModel

URL = "http://localhost:8080/artifactory"
AUTH = ("user", "password_or_apiKey")
PASSWORD = PasswordModel(password="test_password")
API_KEY = ApiKeyModel(apiKey="test_api_key")


class TestSecurity:
    @staticmethod
    @responses.activate
    def test_get_encrypted_password():
        data = PASSWORD.dict()
        data["password"] = PASSWORD.password.get_secret_value()
        responses.add(
            responses.GET,
            f"{URL}/api/security/encryptedPassword",
            json=data,
            status=200,
        )

        artifactory_security = ArtfictorySecurity(AuthModel(url=URL, auth=AUTH))
        enc_pass = artifactory_security.get_encrypted_password()
        assert (
            enc_pass.password.get_secret_value() == PASSWORD.password.get_secret_value()
        )

    @staticmethod
    @responses.activate
    def test_create_api_key():
        data = API_KEY.dict()
        data["apiKey"] = API_KEY.apiKey.get_secret_value()
        responses.add(
            responses.POST, f"{URL}/api/security/apiKey", json=data, status=200
        )

        artifactory_security = ArtfictorySecurity(AuthModel(url=URL, auth=AUTH))
        api_key = artifactory_security.create_api_key()
        assert api_key.apiKey.get_secret_value() == API_KEY.apiKey.get_secret_value()

    @staticmethod
    @responses.activate
    def test_regenerate_api_key():
        data = API_KEY.dict()
        data["apiKey"] = API_KEY.apiKey.get_secret_value()
        responses.add(
            responses.PUT, f"{URL}/api/security/apiKey", json=data, status=200
        )

        artifactory_security = ArtfictorySecurity(AuthModel(url=URL, auth=AUTH))
        api_key = artifactory_security.regenerate_api_key()
        assert api_key.apiKey.get_secret_value() == API_KEY.apiKey.get_secret_value()

    @staticmethod
    @responses.activate
    def test_get_api_key():
        data = API_KEY.dict()
        data["apiKey"] = API_KEY.apiKey.get_secret_value()
        responses.add(
            responses.GET, f"{URL}/api/security/apiKey", json=data, status=200
        )

        artifactory_security = ArtfictorySecurity(AuthModel(url=URL, auth=AUTH))
        api_key = artifactory_security.get_api_key()
        assert api_key.apiKey.get_secret_value() == API_KEY.apiKey.get_secret_value()

    @staticmethod
    @responses.activate
    def test_revoke_api_key():
        responses.add(responses.DELETE, f"{URL}/api/security/apiKey", status=200)

        artifactory_security = ArtfictorySecurity(AuthModel(url=URL, auth=AUTH))
        artifactory_security.revoke_api_key()

    @staticmethod
    @responses.activate
    def test_revoke_user_api_key():
        responses.add(
            responses.DELETE, f"{URL}/api/security/apiKey/test_user", status=200
        )

        artifactory_security = ArtfictorySecurity(AuthModel(url=URL, auth=AUTH))
        artifactory_security.revoke_user_api_key("test_user")
