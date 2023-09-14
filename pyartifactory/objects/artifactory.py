# Copyright (c) 2019 Ananias
# Copyright (c) 2023 Helio Chissini de Castro
#
# Licensed under the MIT license: https://opensource.org/licenses/MIT
# Permission is granted to use, copy, modify, and redistribute the work.
# Full license information available in the project LICENSE file.
#
# SPDX-License-Identifier: MIT
from __future__ import annotations

from pydantic import SecretStr

from pyartifactory.models.auth import AuthModel
from pyartifactory.objects.artifact import ArtifactoryArtifact
from pyartifactory.objects.group import ArtifactoryGroup
from pyartifactory.objects.permission import ArtifactoryPermission
from pyartifactory.objects.repository import ArtifactoryRepository
from pyartifactory.objects.security import ArtifactorySecurity
from pyartifactory.objects.user import ArtifactoryUser


class Artifactory:
    """Models artifactory."""

    def __init__(
        self,
        url: str,
        auth: tuple[str, SecretStr],
        verify: bool = True,
        cert: str | None = None,
        api_version: int = 1,
    ):
        self.artifactory = AuthModel(url=url, auth=auth, verify=verify, cert=cert, api_version=api_version)
        self.users = ArtifactoryUser(self.artifactory)
        self.groups = ArtifactoryGroup(self.artifactory)
        self.security = ArtifactorySecurity(self.artifactory)
        self.repositories = ArtifactoryRepository(self.artifactory)
        self.artifacts = ArtifactoryArtifact(self.artifactory)
        self.permissions = ArtifactoryPermission(self.artifactory)
