from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List


class Checksums(BaseModel):
    sha1: str
    md5: str
    sha256: str


class OriginalChecksums(BaseModel):
    sha256: str


class Child(BaseModel):
    uri: str
    folder: str


class ArtifactPropertiesResponse(BaseModel):
    repo: str
    path: str
    created: Optional[datetime] = None
    createdBy: str
    lastModified: Optional[datetime] = None
    modifiedBy: Optional[str] = None
    lastUpdated: Optional[datetime] = None
    downloadUri: Optional[str] = None
    remoteUrl: Optional[str] = None
    mimeType: Optional[str] = None
    size: Optional[str] = None
    checksums: Optional[Checksums] = None
    originalChecksums: Optional[OriginalChecksums] = None
    children: Optional[List[Child]] = None
    uri: str


class ArtifactStatsResponse(BaseModel):
    uri: str
    downloadCount: int
    lastDownloaded: int
    lastDownloadedBy: Optional[str]
    remoteDownloadCount: int
    remoteLastDownloaded: int
