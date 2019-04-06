import mock

from pyartifactory import ArtfictoryUser
from pyartifactory.models.Auth import AuthModel
from pyartifactory.models.User import NewUser


class TestUser:
    def test_create_user(self):
        url = "http://host:port/artifactory"
        auth = ("user", "password_or_apiKey")
        user = NewUser(
            name="test_user", password="test_password", email="test.test@test.com"
        )

        users_object_mock = mock.create_autospec(
            ArtfictoryUser(AuthModel(url=url, auth=auth)), instance=True
        )
        users_object_mock.create(user)
        users_object_mock.create.assert_called_once_with(user)
        users_object_mock.get.assert_called_once_with(user.name)
