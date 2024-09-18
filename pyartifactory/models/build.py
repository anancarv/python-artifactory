"""
Definition of all build models.
"""
from __future__ import annotations

from typing import Dict, List, Optional

from pydantic import BaseModel, Field


class BuildProperties(BaseModel):
    started: Optional[str] = None
    diff: Optional[str] = None
    project: Optional[str] = None

    # Method to convert model to query string
    def to_query_string(self) -> str:
        # Create a list of key=value pairs for all non-None fields
        properties = [f"{key}={value}" for key, value in self.model_dump(exclude_none=True).items()]

        return "?" + "&".join(properties) if properties else ""


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
    started: str


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


class Vcs(BaseModel):
    revision: Optional[str] = None
    message: Optional[str] = None
    branch: Optional[str] = None
    url: Optional[str] = None


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
    vcs: Optional[List[Vcs]] = None
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

    # Method to extract error message
    def to_error_message(self) -> str:
        return "\n".join([f"Error status: {_error.status} - {_error.message}" for _error in self.errors])


class LicenseControl(BaseModel):
    """Build's license."""

    runChecks: Optional[bool] = None
    includePublishedArtifacts: Optional[bool] = None
    autoDiscover: Optional[bool] = None
    scopesList: Optional[str] = None
    licenseViolationsRecipientsList: Optional[str] = None


class BuildRetention(BaseModel):
    """Build's retention."""

    deleteBuildArtifacts: Optional[bool] = None
    count: Optional[int] = None
    minimumBuildDate: Optional[int] = None
    buildNumbersNotToBeDiscarded: Optional[List[str]] = None


class Artifacts(BaseModel):
    """Build's artifacts."""

    type: Optional[str] = None
    sha1: Optional[str] = None
    md5: Optional[str] = None
    name: Optional[str] = None


class Dependencies(BaseModel):
    """Build's dependency."""

    type: Optional[str] = None
    sha1: Optional[str] = None
    md5: Optional[str] = None
    id: Optional[str] = None
    scopes: Optional[List[str]] = None


class BuildSingleModule(BaseModel):
    """Build's module model."""

    properties: Optional[Dict[str, str]] = None
    id: Optional[str] = None
    artifacts: Optional[List[Artifacts]] = None
    dependencies: Optional[List[Dependencies]] = None


class Tracker(BaseModel):
    """Build's issue tracker."""

    name: Optional[str] = None
    version: Optional[str] = None


class AffectedIssue(BaseModel):
    """Build's affected issue."""

    key: Optional[str] = None
    url: Optional[str] = None
    summary: Optional[str] = None
    aggregated: Optional[bool] = None


class Issue(BaseModel):
    """Build's issue."""

    tracker: Optional[Tracker] = None
    aggregateBuildIssues: Optional[bool] = None
    aggregationBuildStatus: Optional[str] = None
    affectedIssues: Optional[List[AffectedIssue]] = None


class BuildCreateRequest(BaseModel):
    """Models artifactory build creation data."""

    properties: Dict[str, str] = {}
    version: str = "1.0.1"
    name: str
    number: str
    type: Optional[str] = None
    buildAgent: Optional[BuildAgent] = None
    agent: Optional[BuildAgent] = None
    started: str
    artifactoryPluginVersion: Optional[str] = None
    durationMillis: Optional[int] = None
    artifactoryPrincipal: Optional[str] = None
    url: Optional[str] = None
    vcs: Optional[List[Vcs]] = None
    licenseControl: Optional[LicenseControl] = None
    buildRetention: Optional[BuildRetention] = None
    modules: Optional[List[BuildSingleModule]] = None
    issues: Optional[Issue] = None
