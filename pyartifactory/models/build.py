"""
Definition of all build models.
"""
from __future__ import annotations

from typing import Dict, List, Optional

from pydantic import BaseModel, Field


class SimpleBuild(BaseModel):
    """Models an artifactory single build."""

    uri: str
    lastStarted: str


class BuildListResponse(BaseModel):
    """Models all artifactory builds."""

    uri: str = ""
    builds: Optional[List[SimpleBuild]] = None


class Run(BaseModel):
    """Models an artifactory single build run."""

    uri: str
    buildsNumbers: str


class BuildRun(BaseModel):
    """Models artifactory build runs."""

    uri: str
    buildsNumber: Optional[List[Run]] = None


class BuildArtifact(BaseModel):
    """Models artifactory build artifact."""

    type: str
    sha1: str
    sha256: str
    md5: str
    name: str
    path: str


class BuildModules(BaseModel):
    """Models artifactory's build modules."""

    properties: Dict[str, str]
    type: str
    id: str
    artifacts: List[BuildArtifact]


class BuildAgent(BaseModel):
    name: str = ""
    version: str = ""


class BuildInfoDetail(BaseModel):
    """Models artifactory buildInfo dict."""

    properties: Optional[Dict[str, str]] = None
    version: str = ""
    name: str = ""
    number: str = ""
    buildAgent: BuildAgent = BuildAgent()
    agent: BuildAgent = BuildAgent()
    started: str = ""
    durationMillis: int = 0
    artifactoryPrincipal: str = ""
    vcs: Optional[List[Dict[str, str]]] = None
    modules: List[BuildModules] = []


class BuildInfo(BaseModel):
    """Models artifactory build."""

    uri: str = ""
    buildInfo: BuildInfoDetail = BuildInfoDetail()


class BuildPromotionResult(BaseModel):
    messages: List[Dict[str, str]] = []


class BuildPromotionRequest(BaseModel):
    status: str = ""
    comment: str = ""
    ciUser: str = ""
    timestamp: str = ""
    dryRun: bool = False
    sourceRepo: str
    targetRepo: str
    copyArtifact: bool = Field(False, alias="copy")
    artifacts: bool = True
    dependencies: bool = False
    scopes: List[str] = []
    properties: Dict[str, List[str]] = {}
    failFast: bool = True


class BuildDeleteRequest(BaseModel):
    project: str = ""
    buildName: str
    buildNumbers: List[str]
    deleteArtifacts: bool = False
    deleteAll: bool = False


class BuildDiffResponseDetail(BaseModel):
    updated: List[str] = []
    unchanged: List[str] = []
    removed: List[str] = []
    new: List[str] = []


class BuildDiffResponse(BaseModel):
    artifacts: BuildDiffResponseDetail = BuildDiffResponseDetail()
    dependencies: BuildDiffResponseDetail = BuildDiffResponseDetail()
    properties: BuildDiffResponseDetail = BuildDiffResponseDetail()


class BuildErrorDetail(BaseModel):
    status: int = 0
    message: str = ""


class BuildError(BaseModel):
    errors: List[BuildErrorDetail]


class BuildCreateRequest(BaseModel):
    name: str
    number: str
    agent: BuildAgent = BuildAgent()
    buildAgent: BuildAgent = BuildAgent()
    started: str = ""
    properties: Dict[str, str] = {}
    artifactoryPrincipal: str = ""
    vcs: List[Dict[str, str]] = []
