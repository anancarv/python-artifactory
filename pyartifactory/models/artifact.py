"""
Definition of all artifact models.
"""
from __future__ import annotations

import hashlib
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Dict, List, Literal, Optional, Union

from pydantic import BaseModel


class Checksums(BaseModel):
    """Models a checksum."""

    sha1: str
    md5: str
    sha256: str

    @classmethod
    def generate(cls, file_: Path) -> Checksums:
        block_size: int = 65536
        mapping: dict[str, Callable[[], Any]] = {"md5": hashlib.md5, "sha1": hashlib.sha1, "sha256": hashlib.sha256}
        results = {}

        for algorithm, hashing_function in mapping.items():
            hasher = hashing_function()
            with file_.absolute().open("rb") as fd:
                buf = fd.read(block_size)
                while len(buf) > 0:
                    hasher.update(buf)
                    buf = fd.read(block_size)
            results[algorithm] = hasher.hexdigest()

        return cls(**results)


class OriginalChecksums(BaseModel):
    """Models original checksums."""

    sha256: Optional[str] = None
    sha1: Optional[str] = None
    md5: Optional[str] = None


class Child(BaseModel):
    """Models a child folder."""

    uri: str
    folder: bool


class ArtifactPropertiesResponse(BaseModel):
    """Models an artifact properties response."""

    uri: str
    properties: Dict[str, List[str]]


class ArtifactInfoResponseBase(BaseModel):
    """The base information available for both file and folder"""

    repo: str
    path: str
    created: Optional[datetime] = None
    createdBy: Optional[str] = None
    lastModified: Optional[datetime] = None
    modifiedBy: Optional[str] = None
    lastUpdated: Optional[datetime] = None
    uri: str


class ArtifactFolderInfoResponse(ArtifactInfoResponseBase):
    """Models an artifact folder info response."""

    children: List[Child]


class ArtifactFileInfoResponse(ArtifactInfoResponseBase):
    """Models an artifact file info response."""

    downloadUri: Optional[str] = None
    remoteUrl: Optional[str] = None
    mimeType: Optional[str] = None
    size: Optional[int] = None
    checksums: Optional[Checksums] = None
    originalChecksums: Optional[OriginalChecksums] = None


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
    sha1: Optional[str] = None
    sha2: Optional[str] = None


class ArtifactListResponse(BaseModel):
    """Models an artifact list response."""

    uri: str
    created: datetime
    files: List[Union[ArtifactListFileResponse, ArtifactListFolderResponse]]


class ArtifactStatsResponse(BaseModel):
    """Models an artifact statistics response."""

    uri: str
    downloadCount: int
    lastDownloaded: int
    lastDownloadedBy: Optional[str] = None
    remoteDownloadCount: int
    remoteLastDownloaded: int


ArtifactInfoResponse = Union[ArtifactFolderInfoResponse, ArtifactFileInfoResponse]
