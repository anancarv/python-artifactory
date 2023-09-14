# Copyright (c) 2019 Ananias
# Copyright (c) 2023 Helio Chissini de Castro
#
# Licensed under the MIT license: https://opensource.org/licenses/MIT
# Permission is granted to use, copy, modify, and redistribute the work.
# Full license information available in the project LICENSE file.
#
# SPDX-License-Identifier: MIT

"""
Definition of all artifact models.
"""
from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel


class Checksums(BaseModel):
    """Models a checksum."""

    sha1: str
    md5: str
    sha256: str


class OriginalChecksums(BaseModel):
    """Models original checksums."""

    sha256: str


class Child(BaseModel):
    """Models a child folder."""

    uri: str
    folder: bool


class ArtifactPropertiesResponse(BaseModel):
    """Models an artifact properties response."""

    uri: str
    properties: dict[str, list[str]]


class ArtifactInfoResponseBase(BaseModel):
    """The base information available for both file and folder"""

    repo: str
    path: str
    created: datetime | None = None
    createdBy: str | None = None
    lastModified: datetime | None = None
    modifiedBy: str | None = None
    lastUpdated: datetime | None = None
    uri: str


class ArtifactFolderInfoResponse(ArtifactInfoResponseBase):
    """Models an artifact folder info response."""

    children: list[Child]


class ArtifactFileInfoResponse(ArtifactInfoResponseBase):
    """Models an artifact file info response."""

    downloadUri: str | None = None
    remoteUrl: str | None = None
    mimeType: str | None = None
    size: int | None = None
    checksums: Checksums | None = None
    originalChecksums: OriginalChecksums | None = None


class ArtifactListEntryResponse(BaseModel):
    """Base model for an entry in an artifact list response."""

    uri: str
    size: int
    lastModified: datetime
    folder: bool


class ArtifactListFolderResponse(ArtifactListEntryResponse):
    """Models a folder in an artifact list response."""

    folder: Literal[True]


class ArtifactListFileResponse(ArtifactListEntryResponse):
    """Models a file in an artifact list response."""

    folder: Literal[False]
    sha1: str | None = None
    sha2: str | None = None


class ArtifactListResponse(BaseModel):
    """Models an artifact list response."""

    uri: str
    created: datetime
    files: list[ArtifactListFileResponse | ArtifactListFolderResponse]


class ArtifactStatsResponse(BaseModel):
    """Models an artifact statistics response."""

    uri: str
    downloadCount: int
    lastDownloaded: int
    lastDownloadedBy: str | None = None
    remoteDownloadCount: int
    remoteLastDownloaded: int


ArtifactInfoResponse = ArtifactFolderInfoResponse | ArtifactFileInfoResponse
