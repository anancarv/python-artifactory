"""
Definition of all artifact models.
"""
from __future__ import annotations

from datetime import datetime
from typing import Dict, List, Literal, Optional, Union

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
