from typing import Optional, List
from enum import Enum

from pydantic import BaseModel


class PackageTypeEnum(str, Enum):
    maven = "maven"
    gradle = "gradle"
    ivy = "ivy"
    sbt = "sbt"
    helm = "helm"
    cocoapods = "cocoapods"
    opkg = "opkg"
    rpm = "rpm"
    nuget = "nuget"
    cran = "cran"
    gems = "gems"
    npm = "npm"
    bower = "bower"
    debian = "debian"
    pypi = "pypi"
    docker = "docker"
    yum = "yum"
    vcs = "vcs"
    composer = "composer"
    go = "go"
    p2 = "p2"
    chef = "chef"
    puppet = "puppet"
    generic = "generic"


class RClassEnum(str, Enum):
    local = "local"
    virtual = "virtual"
    remote = "remote"


class ChecksumPolicyType(str, Enum):
    client_checksums = "client-checksums"
    server_generated_checksums = "server-generated-checksums"


class SnapshotVersionBehavior(str, Enum):
    unique = "unique"
    non_unique = "non-unique"
    deployer = "deployer"


class PomRepoRefCleanupPolicy(str, Enum):
    discard_active_reference = "discard_active_reference"
    discard_any_reference = "discard_any_reference"
    nothing = "nothing"


class SimpleRepository(BaseModel):
    key: str
    type: str
    description: Optional[str] = None
    url: str
    packageType: str


class BaseRepositoryModel(BaseModel):
    key: str
    rclass: RClassEnum = RClassEnum.local
    packageType: PackageTypeEnum = PackageTypeEnum.generic
    description: Optional[str] = None
    notes: Optional[str] = None
    includesPattern: str = "**/*"
    excludesPattern: str = ""
    repoLayoutRef: str = "maven-2-default"
    debianTrivialLayout: bool = False


class LocalRepository(BaseRepositoryModel):
    checksumPolicyType: ChecksumPolicyType = ChecksumPolicyType.client_checksums
    handleReleases: bool = True
    handleSnapshots: bool = True
    maxUniqueSnapshots: int = 0
    maxUniqueTags: int = 0
    snapshotVersionBehavior: SnapshotVersionBehavior = SnapshotVersionBehavior.non_unique
    suppressPomConsistencyChecks: bool = False
    blackedOut: bool = False
    xrayIndex: bool = False
    propertySets: List[str] = None
    archiveBrowsingEnabled: bool = False
    calculateYumMetadata: bool = False
    yumRootDepth: int = 0
    dockerApiVersion: str = "V2"
    enableFileListsIndexing: str = "false"
    optionalIndexCompressionFormats: List[str] = None
    downloadRedirect: str = "false"


class VirtualRepository(BaseRepositoryModel):
    artifactoryRequestsCanRetrieveRemoteArtifacts: bool = False
    keyPair: Optional[str] = None
    pomRepositoryReferencesCleanupPolicy: PomRepoRefCleanupPolicy = PomRepoRefCleanupPolicy.discard_active_reference
    defaultDeploymentRepo: Optional[str] = None
    forceMavenAuthentication: bool = False
    externalDependenciesEnabled: bool = False
    externalDependenciesPatterns: List[str] = None
    externalDependenciesRemoteRepo: str = None


class RemoteRepository(BaseRepositoryModel):
    # ToDo
    pass


class RepositoryList(BaseModel):
    repositories: List[SimpleRepository] = None
