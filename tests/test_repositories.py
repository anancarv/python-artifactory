# Copyright (c) 2019 Ananias
# Copyright (c) 2023 Helio Chissini de Castro
#
# Licensed under the MIT license: https://opensource.org/licenses/MIT
# Permission is granted to use, copy, modify, and redistribute the work.
# Full license information available in the project LICENSE file.
#
# SPDX-License-Identifier: MIT
from __future__ import annotations

import pytest
import requests
import responses

from pyartifactory import ArtifactoryRepository
from pyartifactory.exception import RepositoryAlreadyExistsError, RepositoryNotFoundError
from pyartifactory.models import (
    AuthModel,
    LocalRepository,
    LocalRepositoryResponse,
    RemoteRepository,
    RemoteRepositoryResponse,
    SimpleRepository,
    VirtualRepository,
    VirtualRepositoryResponse,
)

URL = "http://localhost:8080/artifactory"
AUTH = ("user", "password_or_apiKey")

SIMPLE_REPOSITORY = SimpleRepository(key="test_repository", type_="local", url="some-url", packageType="docker")
LOCAL_REPOSITORY = LocalRepository(key="test_local_repository")
LOCAL_REPOSITORY_RESPONSE = LocalRepositoryResponse(key="test_local_repository")
UPDATED_LOCAL_REPOSITORY = LocalRepository(key="test_local_repository", description="updated")
UPDATED_LOCAL_REPOSITORY_RESPONSE = LocalRepositoryResponse(key="test_local_repository", description="updated")
VIRTUAL_REPOSITORY = VirtualRepository(key="test_virtual_repository")
VIRTUAL_REPOSITORY_RESPONSE = VirtualRepositoryResponse(key="test_virtual_repository")
UPDATED_VIRTUAL_REPOSITORY = VirtualRepository(key="test_virtual_repository", description="updated")
UPDATED_VIRTUAL_REPOSITORY_RESPONSE = VirtualRepositoryResponse(key="test_virtual_repository", description="updated")
REMOTE_REPOSITORY = RemoteRepository(key="test_remote_repository", url="http://test-url.com")
REMOTE_REPOSITORY_RESPONSE = RemoteRepositoryResponse(key="test_remote_repository", url="http://test-url.com")
UPDATED_REMOTE_REPOSITORY = RemoteRepository(
    key="test_remote_repository",
    url="http://test-url.com",
    description="updated",
)
UPDATED_REMOTE_REPOSITORY_RESPONSE = RemoteRepositoryResponse(
    key="test_remote_repository",
    url="http://test-url.com",
    description="updated",
)


@responses.activate
def test_create_local_repository_using_create_repo_fail_if_repository_already_exists(
    mocker,
):
    responses.add(
        responses.GET,
        f"{URL}/api/repositories/{LOCAL_REPOSITORY.key}",
        json=LOCAL_REPOSITORY_RESPONSE.model_dump(),
        status=200,
    )

    artifactory_repo = ArtifactoryRepository(AuthModel(url=URL, auth=AUTH))
    mocker.spy(artifactory_repo, "get_repo")
    with pytest.raises(RepositoryAlreadyExistsError):
        artifactory_repo.create_repo(LOCAL_REPOSITORY)

    artifactory_repo.get_repo.assert_called_once_with(LOCAL_REPOSITORY.key)


@responses.activate
def test_create_local_repository_fail_if_repository_already_exists(mocker):
    responses.add(
        responses.GET,
        f"{URL}/api/repositories/{LOCAL_REPOSITORY.key}",
        json=LOCAL_REPOSITORY_RESPONSE.model_dump(),
        status=200,
    )

    artifactory_repo = ArtifactoryRepository(AuthModel(url=URL, auth=AUTH))
    mocker.spy(artifactory_repo, "get_local_repo")
    with pytest.raises(RepositoryAlreadyExistsError):
        artifactory_repo.create_local_repo(LOCAL_REPOSITORY)

    artifactory_repo.get_local_repo.assert_called_once_with(LOCAL_REPOSITORY.key)


@responses.activate
def test_create_virtual_repository_using_create_repo_fail_if_repository_already_exists(
    mocker,
):
    responses.add(
        responses.GET,
        f"{URL}/api/repositories/{VIRTUAL_REPOSITORY.key}",
        json=VIRTUAL_REPOSITORY_RESPONSE.model_dump(),
        status=200,
    )

    artifactory_repo = ArtifactoryRepository(AuthModel(url=URL, auth=AUTH))
    mocker.spy(artifactory_repo, "get_repo")
    with pytest.raises(RepositoryAlreadyExistsError):
        artifactory_repo.create_repo(VIRTUAL_REPOSITORY)

    artifactory_repo.get_repo.assert_called_once_with(VIRTUAL_REPOSITORY.key)


@responses.activate
def test_create_virtual_repository_fail_if_repository_already_exists(mocker):
    responses.add(
        responses.GET,
        f"{URL}/api/repositories/{VIRTUAL_REPOSITORY.key}",
        json=VIRTUAL_REPOSITORY_RESPONSE.model_dump(),
        status=200,
    )

    artifactory_repo = ArtifactoryRepository(AuthModel(url=URL, auth=AUTH))
    mocker.spy(artifactory_repo, "get_virtual_repo")
    with pytest.raises(RepositoryAlreadyExistsError):
        artifactory_repo.create_virtual_repo(VIRTUAL_REPOSITORY)

    artifactory_repo.get_virtual_repo.assert_called_once_with(VIRTUAL_REPOSITORY.key)


@responses.activate
def test_create_remote_repository_using_create_repo_fail_if_repository_already_exists(
    mocker,
):
    responses.add(
        responses.GET,
        f"{URL}/api/repositories/{REMOTE_REPOSITORY.key}",
        json=REMOTE_REPOSITORY_RESPONSE.model_dump(),
        status=200,
    )

    artifactory_repo = ArtifactoryRepository(AuthModel(url=URL, auth=AUTH))
    mocker.spy(artifactory_repo, "get_repo")
    with pytest.raises(RepositoryAlreadyExistsError):
        artifactory_repo.create_repo(REMOTE_REPOSITORY)

    artifactory_repo.get_repo.assert_called_once_with(REMOTE_REPOSITORY.key)


@responses.activate
def test_create_remote_repository_fail_if_repository_already_exists(mocker):
    responses.add(
        responses.GET,
        f"{URL}/api/repositories/{REMOTE_REPOSITORY.key}",
        json=REMOTE_REPOSITORY_RESPONSE.model_dump(),
        status=200,
    )

    artifactory_repo = ArtifactoryRepository(AuthModel(url=URL, auth=AUTH))
    mocker.spy(artifactory_repo, "get_remote_repo")
    with pytest.raises(RepositoryAlreadyExistsError):
        artifactory_repo.create_remote_repo(REMOTE_REPOSITORY)

    artifactory_repo.get_remote_repo.assert_called_once_with(REMOTE_REPOSITORY.key)


@responses.activate
def test_create_local_repository_using_create_repo_success(mocker):
    responses.add(responses.GET, f"{URL}/api/repositories/{LOCAL_REPOSITORY.key}", status=404)
    responses.add(
        responses.PUT,
        f"{URL}/api/repositories/{LOCAL_REPOSITORY.key}",
        json=LOCAL_REPOSITORY_RESPONSE.model_dump(),
        status=201,
    )
    responses.add(
        responses.GET,
        f"{URL}/api/repositories/{LOCAL_REPOSITORY.key}",
        json=LOCAL_REPOSITORY_RESPONSE.model_dump(),
        status=200,
    )

    artifactory_repo = ArtifactoryRepository(AuthModel(url=URL, auth=AUTH))
    mocker.spy(artifactory_repo, "get_repo")
    local_repo = artifactory_repo.create_repo(LOCAL_REPOSITORY)

    assert isinstance(local_repo, LocalRepositoryResponse)
    assert local_repo == LOCAL_REPOSITORY_RESPONSE


@responses.activate
def test_create_local_repository_success(mocker):
    responses.add(responses.GET, f"{URL}/api/repositories/{LOCAL_REPOSITORY.key}", status=404)
    responses.add(
        responses.PUT,
        f"{URL}/api/repositories/{LOCAL_REPOSITORY.key}",
        json=LOCAL_REPOSITORY_RESPONSE.model_dump(),
        status=201,
    )
    responses.add(
        responses.GET,
        f"{URL}/api/repositories/{LOCAL_REPOSITORY.key}",
        json=LOCAL_REPOSITORY_RESPONSE.model_dump(),
        status=200,
    )

    artifactory_repo = ArtifactoryRepository(AuthModel(url=URL, auth=AUTH))
    mocker.spy(artifactory_repo, "get_local_repo")
    local_repo = artifactory_repo.create_local_repo(LOCAL_REPOSITORY)

    artifactory_repo.get_local_repo.assert_called_with(LOCAL_REPOSITORY.key)
    assert artifactory_repo.get_local_repo.call_count == 2
    assert local_repo == LOCAL_REPOSITORY_RESPONSE


@responses.activate
def test_create_virtual_repository_using_create_repo_success(mocker):
    responses.add(responses.GET, f"{URL}/api/repositories/{VIRTUAL_REPOSITORY.key}", status=404)
    responses.add(
        responses.PUT,
        f"{URL}/api/repositories/{VIRTUAL_REPOSITORY.key}",
        json=VIRTUAL_REPOSITORY_RESPONSE.model_dump(),
        status=201,
    )
    responses.add(
        responses.GET,
        f"{URL}/api/repositories/{VIRTUAL_REPOSITORY.key}",
        json=VIRTUAL_REPOSITORY_RESPONSE.model_dump(),
        status=200,
    )

    artifactory_repo = ArtifactoryRepository(AuthModel(url=URL, auth=AUTH))
    mocker.spy(artifactory_repo, "get_repo")
    virtual_repo = artifactory_repo.create_repo(VIRTUAL_REPOSITORY)

    assert virtual_repo == VIRTUAL_REPOSITORY_RESPONSE


@responses.activate
def test_create_virtual_repository_success(mocker):
    responses.add(responses.GET, f"{URL}/api/repositories/{VIRTUAL_REPOSITORY.key}", status=404)
    responses.add(
        responses.PUT,
        f"{URL}/api/repositories/{VIRTUAL_REPOSITORY.key}",
        json=VIRTUAL_REPOSITORY_RESPONSE.model_dump(),
        status=201,
    )
    responses.add(
        responses.GET,
        f"{URL}/api/repositories/{VIRTUAL_REPOSITORY.key}",
        json=VIRTUAL_REPOSITORY_RESPONSE.model_dump(),
        status=200,
    )

    artifactory_repo = ArtifactoryRepository(AuthModel(url=URL, auth=AUTH))
    mocker.spy(artifactory_repo, "get_virtual_repo")
    virtual_repo = artifactory_repo.create_virtual_repo(VIRTUAL_REPOSITORY)

    artifactory_repo.get_virtual_repo.assert_called_with(VIRTUAL_REPOSITORY.key)
    assert artifactory_repo.get_virtual_repo.call_count == 2
    assert virtual_repo.model_dump() == VIRTUAL_REPOSITORY_RESPONSE.model_dump()


@responses.activate
def test_create_remote_repository_using_create_repo_success(mocker):
    responses.add(responses.GET, f"{URL}/api/repositories/{REMOTE_REPOSITORY.key}", status=404)
    responses.add(
        responses.PUT,
        f"{URL}/api/repositories/{REMOTE_REPOSITORY.key}",
        json=REMOTE_REPOSITORY_RESPONSE.model_dump(),
        status=201,
    )
    responses.add(
        responses.GET,
        f"{URL}/api/repositories/{REMOTE_REPOSITORY.key}",
        json=REMOTE_REPOSITORY_RESPONSE.model_dump(),
        status=200,
    )

    artifactory_repo = ArtifactoryRepository(AuthModel(url=URL, auth=AUTH))
    mocker.spy(artifactory_repo, "get_repo")
    remote_repo = artifactory_repo.create_repo(REMOTE_REPOSITORY)

    assert remote_repo == REMOTE_REPOSITORY_RESPONSE


@responses.activate
def test_create_remote_repository_success(mocker):
    responses.add(responses.GET, f"{URL}/api/repositories/{REMOTE_REPOSITORY.key}", status=404)
    responses.add(
        responses.PUT,
        f"{URL}/api/repositories/{REMOTE_REPOSITORY.key}",
        json=REMOTE_REPOSITORY_RESPONSE.model_dump(),
        status=201,
    )
    responses.add(
        responses.GET,
        f"{URL}/api/repositories/{REMOTE_REPOSITORY.key}",
        json=REMOTE_REPOSITORY_RESPONSE.model_dump(),
        status=200,
    )

    artifactory_repo = ArtifactoryRepository(AuthModel(url=URL, auth=AUTH))
    mocker.spy(artifactory_repo, "get_remote_repo")
    remote_repo = artifactory_repo.create_remote_repo(REMOTE_REPOSITORY)

    artifactory_repo.get_remote_repo.assert_called_with(REMOTE_REPOSITORY.key)
    assert artifactory_repo.get_remote_repo.call_count == 2
    assert remote_repo == REMOTE_REPOSITORY_RESPONSE


@responses.activate
def test_get_local_repository_using_get_repo_error_not_found(mocker):
    responses.add(responses.GET, f"{URL}/api/repositories/{LOCAL_REPOSITORY.key}", status=404)

    artifactory_repo = ArtifactoryRepository(AuthModel(url=URL, auth=AUTH))
    mocker.spy(artifactory_repo, "get_repo")
    with pytest.raises(RepositoryNotFoundError):
        artifactory_repo.get_repo(LOCAL_REPOSITORY.key)


@responses.activate
def test_get_local_repository_error_not_found():
    responses.add(responses.GET, f"{URL}/api/repositories/{LOCAL_REPOSITORY.key}", status=404)

    artifactory_repo = ArtifactoryRepository(AuthModel(url=URL, auth=AUTH))
    with pytest.raises(RepositoryNotFoundError):
        artifactory_repo.get_local_repo(LOCAL_REPOSITORY.key)


@responses.activate
def test_get_virtual_repository_error_not_found():
    responses.add(responses.GET, f"{URL}/api/repositories/{VIRTUAL_REPOSITORY.key}", status=404)

    artifactory_repo = ArtifactoryRepository(AuthModel(url=URL, auth=AUTH))
    with pytest.raises(RepositoryNotFoundError):
        artifactory_repo.get_virtual_repo(VIRTUAL_REPOSITORY.key)


@responses.activate
def test_get_remote_repository_error_not_found():
    responses.add(responses.GET, f"{URL}/api/repositories/{REMOTE_REPOSITORY.key}", status=404)

    artifactory_repo = ArtifactoryRepository(AuthModel(url=URL, auth=AUTH))
    with pytest.raises(RepositoryNotFoundError):
        artifactory_repo.get_remote_repo(REMOTE_REPOSITORY.key)


@responses.activate
def test_get_local_repository_using_get_repo_success():
    responses.add(
        responses.GET,
        f"{URL}/api/repositories/{LOCAL_REPOSITORY.key}",
        json=LOCAL_REPOSITORY_RESPONSE.model_dump(),
        status=200,
    )

    artifactory_repo = ArtifactoryRepository(AuthModel(url=URL, auth=AUTH))
    local_repo = artifactory_repo.get_repo(LOCAL_REPOSITORY.key)

    assert local_repo == LOCAL_REPOSITORY_RESPONSE


@responses.activate
def test_get_local_repository_success(mocker):
    responses.add(
        responses.GET,
        f"{URL}/api/repositories/{LOCAL_REPOSITORY.key}",
        json=LOCAL_REPOSITORY_RESPONSE.model_dump(),
        status=200,
    )

    artifactory_repo = ArtifactoryRepository(AuthModel(url=URL, auth=AUTH))
    mocker.spy(artifactory_repo, "get_local_repo")
    local_repo = artifactory_repo.get_local_repo(LOCAL_REPOSITORY.key)

    artifactory_repo.get_local_repo.assert_called_once()
    assert local_repo == LOCAL_REPOSITORY_RESPONSE


@responses.activate
def test_get_virtual_repository_using_get_repo_success(mocker):
    responses.add(
        responses.GET,
        f"{URL}/api/repositories/{VIRTUAL_REPOSITORY.key}",
        json=VIRTUAL_REPOSITORY_RESPONSE.model_dump(),
        status=200,
    )

    artifactory_repo = ArtifactoryRepository(AuthModel(url=URL, auth=AUTH))
    virtual_repo = artifactory_repo.get_repo(VIRTUAL_REPOSITORY.key)

    assert virtual_repo == VIRTUAL_REPOSITORY_RESPONSE


@responses.activate
def test_get_virtual_repository_success(mocker):
    responses.add(
        responses.GET,
        f"{URL}/api/repositories/{VIRTUAL_REPOSITORY.key}",
        json=VIRTUAL_REPOSITORY_RESPONSE.model_dump(),
        status=200,
    )

    artifactory_repo = ArtifactoryRepository(AuthModel(url=URL, auth=AUTH))
    mocker.spy(artifactory_repo, "get_virtual_repo")
    virtual_repo = artifactory_repo.get_virtual_repo(VIRTUAL_REPOSITORY.key)

    artifactory_repo.get_virtual_repo.assert_called_once()
    assert virtual_repo == VIRTUAL_REPOSITORY_RESPONSE


@responses.activate
def test_get_remote_repository_using_get_repo_success():
    responses.add(
        responses.GET,
        f"{URL}/api/repositories/{REMOTE_REPOSITORY.key}",
        json=REMOTE_REPOSITORY_RESPONSE.model_dump(),
        status=200,
    )

    artifactory_repo = ArtifactoryRepository(AuthModel(url=URL, auth=AUTH))
    remote_repo = artifactory_repo.get_repo(REMOTE_REPOSITORY.key)

    assert remote_repo == REMOTE_REPOSITORY_RESPONSE


@responses.activate
def test_get_remote_repository_success(mocker):
    responses.add(
        responses.GET,
        f"{URL}/api/repositories/{REMOTE_REPOSITORY.key}",
        json=REMOTE_REPOSITORY_RESPONSE.model_dump(),
        status=200,
    )

    artifactory_repo = ArtifactoryRepository(AuthModel(url=URL, auth=AUTH))
    mocker.spy(artifactory_repo, "get_remote_repo")
    remote_repo = artifactory_repo.get_remote_repo(REMOTE_REPOSITORY.key)

    artifactory_repo.get_remote_repo.assert_called_once()
    assert remote_repo == REMOTE_REPOSITORY_RESPONSE


@responses.activate
def test_list_repositories_success(mocker):
    responses.add(
        responses.GET,
        f"{URL}/api/repositories",
        json=[SIMPLE_REPOSITORY.model_dump()],
        status=200,
    )

    artifactory_repo = ArtifactoryRepository(AuthModel(url=URL, auth=AUTH))
    mocker.spy(artifactory_repo, "list_all")
    artifactory_repo.list_all()

    artifactory_repo.list_all.assert_called_once()


@responses.activate
def test_update_local_repository_using_update_repo_fail_if_repo_not_found(mocker):
    responses.add(responses.GET, f"{URL}/api/repositories/{LOCAL_REPOSITORY.key}", status=404)

    artifactory_repo = ArtifactoryRepository(AuthModel(url=URL, auth=AUTH))
    mocker.spy(artifactory_repo, "get_repo")
    with pytest.raises(RepositoryNotFoundError):
        artifactory_repo.update_repo(LOCAL_REPOSITORY)
    artifactory_repo.get_repo.assert_called_once_with(LOCAL_REPOSITORY.key)


@responses.activate
def test_update_local_repository_fail_if_repo_not_found(mocker):
    responses.add(responses.GET, f"{URL}/api/repositories/{LOCAL_REPOSITORY.key}", status=404)

    artifactory_repo = ArtifactoryRepository(AuthModel(url=URL, auth=AUTH))
    mocker.spy(artifactory_repo, "get_local_repo")
    with pytest.raises(RepositoryNotFoundError):
        artifactory_repo.update_local_repo(LOCAL_REPOSITORY)

    artifactory_repo.get_local_repo.assert_called_once_with(LOCAL_REPOSITORY.key)


@responses.activate
def test_update_virtual_repository_using_update_repo_fail_if_repo_not_found(mocker):
    responses.add(responses.GET, f"{URL}/api/repositories/{VIRTUAL_REPOSITORY.key}", status=404)

    artifactory_repo = ArtifactoryRepository(AuthModel(url=URL, auth=AUTH))
    mocker.spy(artifactory_repo, "get_repo")
    with pytest.raises(RepositoryNotFoundError):
        artifactory_repo.update_repo(VIRTUAL_REPOSITORY)

    artifactory_repo.get_repo.assert_called_once_with(VIRTUAL_REPOSITORY.key)


@responses.activate
def test_update_virtual_repository_fail_if_repo_not_found(mocker):
    responses.add(responses.GET, f"{URL}/api/repositories/{VIRTUAL_REPOSITORY.key}", status=404)

    artifactory_repo = ArtifactoryRepository(AuthModel(url=URL, auth=AUTH))
    mocker.spy(artifactory_repo, "get_virtual_repo")
    with pytest.raises(RepositoryNotFoundError):
        artifactory_repo.update_virtual_repo(VIRTUAL_REPOSITORY)

    artifactory_repo.get_virtual_repo.assert_called_once_with(VIRTUAL_REPOSITORY.key)


@responses.activate
def test_update_remote_repository_using_update_repo_fail_if_repo_not_found(mocker):
    responses.add(responses.GET, f"{URL}/api/repositories/{REMOTE_REPOSITORY.key}", status=404)

    artifactory_repo = ArtifactoryRepository(AuthModel(url=URL, auth=AUTH))
    mocker.spy(artifactory_repo, "get_repo")
    with pytest.raises(RepositoryNotFoundError):
        artifactory_repo.update_repo(REMOTE_REPOSITORY)

    artifactory_repo.get_repo.assert_called_once_with(REMOTE_REPOSITORY.key)


@responses.activate
def test_update_remote_repository_fail_if_repo_not_found(mocker):
    responses.add(responses.GET, f"{URL}/api/repositories/{REMOTE_REPOSITORY.key}", status=404)

    artifactory_repo = ArtifactoryRepository(AuthModel(url=URL, auth=AUTH))
    mocker.spy(artifactory_repo, "get_remote_repo")
    with pytest.raises(RepositoryNotFoundError):
        artifactory_repo.update_remote_repo(REMOTE_REPOSITORY)

    artifactory_repo.get_remote_repo.assert_called_once_with(REMOTE_REPOSITORY.key)


@responses.activate
def test_update_local_repository_using_update_repo_success(mocker):
    responses.add(
        responses.GET,
        f"{URL}/api/repositories/{UPDATED_LOCAL_REPOSITORY.key}",
        json=UPDATED_LOCAL_REPOSITORY_RESPONSE.model_dump(),
        status=200,
    )

    responses.add(
        responses.POST,
        f"{URL}/api/repositories/{UPDATED_LOCAL_REPOSITORY.key}",
        status=200,
    )
    responses.add(
        responses.GET,
        f"{URL}/api/repositories/{UPDATED_LOCAL_REPOSITORY.key}",
        json=UPDATED_LOCAL_REPOSITORY_RESPONSE.model_dump(),
        status=200,
    )
    artifactory_repo = ArtifactoryRepository(AuthModel(url=URL, auth=AUTH))
    mocker.spy(artifactory_repo, "get_repo")
    updated_repo = artifactory_repo.update_repo(UPDATED_LOCAL_REPOSITORY)

    assert isinstance(updated_repo, LocalRepositoryResponse)
    assert updated_repo == UPDATED_LOCAL_REPOSITORY_RESPONSE


@responses.activate
def test_update_local_repository_success(mocker):
    responses.add(
        responses.GET,
        f"{URL}/api/repositories/{LOCAL_REPOSITORY.key}",
        json=LOCAL_REPOSITORY_RESPONSE.model_dump(),
        status=200,
    )

    responses.add(
        responses.POST,
        f"{URL}/api/repositories/{LOCAL_REPOSITORY.key}",
        json=LOCAL_REPOSITORY_RESPONSE.model_dump(),
        status=200,
    )
    artifactory_repo = ArtifactoryRepository(AuthModel(url=URL, auth=AUTH))
    mocker.spy(artifactory_repo, "get_local_repo")
    artifactory_repo.update_local_repo(LOCAL_REPOSITORY)

    artifactory_repo.get_local_repo.assert_called_with(LOCAL_REPOSITORY.key)
    assert artifactory_repo.get_local_repo.call_count == 2


@responses.activate
def test_update_virtual_repository_using_update_repo_success():
    responses.add(
        responses.GET,
        f"{URL}/api/repositories/{UPDATED_VIRTUAL_REPOSITORY.key}",
        json=VIRTUAL_REPOSITORY_RESPONSE.model_dump(),
        status=200,
    )

    responses.add(
        responses.POST,
        f"{URL}/api/repositories/{UPDATED_VIRTUAL_REPOSITORY.key}",
        status=200,
    )
    responses.add(
        responses.GET,
        f"{URL}/api/repositories/{UPDATED_VIRTUAL_REPOSITORY.key}",
        json=UPDATED_VIRTUAL_REPOSITORY_RESPONSE.model_dump(),
        status=200,
    )
    artifactory_repo = ArtifactoryRepository(AuthModel(url=URL, auth=AUTH))
    updated_repo = artifactory_repo.update_repo(UPDATED_VIRTUAL_REPOSITORY)
    assert updated_repo == UPDATED_VIRTUAL_REPOSITORY_RESPONSE


@responses.activate
def test_update_virtual_repository_success(mocker):
    responses.add(
        responses.GET,
        f"{URL}/api/repositories/{VIRTUAL_REPOSITORY.key}",
        json=VIRTUAL_REPOSITORY_RESPONSE.model_dump(),
        status=200,
    )

    responses.add(
        responses.POST,
        f"{URL}/api/repositories/{VIRTUAL_REPOSITORY.key}",
        status=200,
    )
    artifactory_repo = ArtifactoryRepository(AuthModel(url=URL, auth=AUTH))
    mocker.spy(artifactory_repo, "get_virtual_repo")
    artifactory_repo.update_virtual_repo(VIRTUAL_REPOSITORY)

    artifactory_repo.get_virtual_repo.assert_called_with(VIRTUAL_REPOSITORY.key)
    assert artifactory_repo.get_virtual_repo.call_count == 2


@responses.activate
def test_update_remote_repository_using_update_repo_success():
    responses.add(
        responses.GET,
        f"{URL}/api/repositories/{UPDATED_REMOTE_REPOSITORY.key}",
        json=UPDATED_REMOTE_REPOSITORY_RESPONSE.model_dump(),
        status=200,
    )

    responses.add(
        responses.POST,
        f"{URL}/api/repositories/{UPDATED_REMOTE_REPOSITORY.key}",
        status=200,
    )
    responses.add(
        responses.GET,
        f"{URL}/api/repositories/{UPDATED_REMOTE_REPOSITORY.key}",
        json=UPDATED_REMOTE_REPOSITORY_RESPONSE.model_dump(),
        status=200,
    )
    artifactory_repo = ArtifactoryRepository(AuthModel(url=URL, auth=AUTH))
    updated_repo = artifactory_repo.update_repo(UPDATED_REMOTE_REPOSITORY)
    assert updated_repo == UPDATED_REMOTE_REPOSITORY_RESPONSE


@responses.activate
def test_update_remote_repository_success(mocker):
    responses.add(
        responses.GET,
        f"{URL}/api/repositories/{REMOTE_REPOSITORY.key}",
        json=REMOTE_REPOSITORY_RESPONSE.model_dump(),
        status=200,
    )

    responses.add(
        responses.POST,
        f"{URL}/api/repositories/{REMOTE_REPOSITORY.key}",
        json=REMOTE_REPOSITORY_RESPONSE.model_dump(),
        status=200,
    )
    artifactory_repo = ArtifactoryRepository(AuthModel(url=URL, auth=AUTH))
    mocker.spy(artifactory_repo, "get_remote_repo")
    artifactory_repo.update_remote_repo(REMOTE_REPOSITORY)

    artifactory_repo.get_remote_repo.assert_called_with(REMOTE_REPOSITORY.key)
    assert artifactory_repo.get_remote_repo.call_count == 2


@responses.activate
def test_delete_repo_fail_if_repo_not_found():
    responses.add(responses.DELETE, f"{URL}/api/repositories/{REMOTE_REPOSITORY.key}", status=404)

    artifactory_repo = ArtifactoryRepository(AuthModel(url=URL, auth=AUTH))

    with pytest.raises(requests.exceptions.HTTPError):
        artifactory_repo.delete(REMOTE_REPOSITORY.key)


@responses.activate
def test_delete_repo_success():
    responses.add(responses.DELETE, f"{URL}/api/repositories/{VIRTUAL_REPOSITORY.key}", status=204)
    artifactory_repo = ArtifactoryRepository(AuthModel(url=URL, auth=AUTH))
    artifactory_repo.delete(VIRTUAL_REPOSITORY.key)
