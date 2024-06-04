"""
Definition of all repository models.
"""
from __future__ import annotations

from enum import Enum
from typing import List, Literal, Optional

from pydantic import BaseModel, SecretStr


class PackageTypeEnum(str, Enum):
    """Enumerates package types."""

    alpine = "alpine"
    bower = "bower"
    cargo = "cargo"
    chef = "chef"
    cocoapods = "cocoapods"
    composer = "composer"
    conan = "conan"
    conda = "conda"
    cran = "cran"
    debian = "debian"
    docker = "docker"
    gems = "gems"
    generic = "generic"
    gitlfs = "gitlfs"
    go = "go"
    gradle = "gradle"
    helm = "helm"
    helmoci = "helmoci"
    ivy = "ivy"
    maven = "maven"
    npm = "npm"
    nuget = "nuget"
    opkg = "opkg"
    p2 = "p2"
    puppet = "puppet"
    pypi = "pypi"
    rpm = "rpm"
    sbt = "sbt"
    terraform = "terraform"
    terraformbackend = "terraformbackend"
    vagrant = "vagrant"
    vcs = "vcs"
    yum = "yum"


class RClassEnum(str, Enum):
    """Enumerates remote types."""

    local = "local"
    virtual = "virtual"
    remote = "remote"
    federated = "federated"


class ChecksumPolicyType(str, Enum):
    """Enumerates checksum policy types."""

    client_checksums = "client-checksums"
    server_generated_checksums = "server-generated-checksums"


class SnapshotVersionBehavior(str, Enum):
    """Enumerates snapshot version behavior options."""

    unique = "unique"
    non_unique = "non-unique"
    deployer = "deployer"


class PomRepoRefCleanupPolicy(str, Enum):
    """Models a repo reference cleanup policy."""

    discard_active_reference = "discard_active_reference"
    discard_any_reference = "discard_any_reference"
    nothing = "nothing"


class VcsGitProviderEnum(str, Enum):
    """Enumerates the available vcs providers."""

    github = "GITHUB"
    bitbucket = "BITBUCKET"
    oldstash = "OLDSTASH"
    stash = "STASH"
    artifactory = "ARTIFACTORY"
    custom = "CUSTOM"


class Statistics(BaseModel):
    """Models statistics."""

    enabled: bool = False


class Properties(BaseModel):
    """Models properties."""

    enabled: bool = False


class Source(BaseModel):
    """Models a source."""

    originAbsenceDetection: bool = False


class ContentSynchronisation(BaseModel):
    """Models a content synchronization."""

    enabled: bool = False
    statistics: Statistics = Statistics()
    properties: Properties = Properties()
    source: Source = Source()


class FederatedMembers(BaseModel):
    url: str = ""
    enabled: Literal["true", "false"] = "true"


class FederatedMembersResponse(BaseModel):
    """Models a federated member response."""

    url: str = ""
    enabled: bool = True


class SimpleRepository(BaseModel):
    """Models a simple repository."""

    key: str
    type: str
    description: Optional[str] = None
    url: str
    packageType: str


class BaseRepositoryModel(BaseModel):
    """Models a base repository."""

    key: str
    projectKey: Optional[str] = None
    rclass: RClassEnum
    packageType: PackageTypeEnum = PackageTypeEnum.generic
    description: Optional[str] = None
    notes: Optional[str] = None
    includesPattern: str = "**/*"
    excludesPattern: str = ""
    repoLayoutRef: str = "maven-2-default"


class LocalRepository(BaseRepositoryModel):
    """Models a local repository."""

    rclass: Literal[RClassEnum.local] = RClassEnum.local
    checksumPolicyType: ChecksumPolicyType = ChecksumPolicyType.client_checksums
    handleReleases: bool = True
    handleSnapshots: bool = True
    maxUniqueSnapshots: int = 0
    maxUniqueTags: int = 0
    debianTrivialLayout: bool = False
    snapshotVersionBehavior: SnapshotVersionBehavior = SnapshotVersionBehavior.non_unique
    suppressPomConsistencyChecks: bool = False
    blackedOut: bool = False
    xrayIndex: bool = False
    propertySets: Optional[List[str]] = None
    dockerApiVersion: str = "V2"
    archiveBrowsingEnabled: bool = False
    calculateYumMetadata: bool = False
    yumRootDepth: int = 0
    enableFileListsIndexing: bool = False
    optionalIndexCompressionFormats: Optional[List[str]] = None
    downloadRedirect: bool = False
    cdnRedirect: bool = False
    blockPushingSchema1: bool = False
    primaryKeyPairRef: Optional[str] = None
    secondaryKeyPairRef: Optional[str] = None
    priorityResolution: bool = False
    cargoInternalIndex: bool = False
    terraformType: Literal["MODULE", "PROVIDER"] = "MODULE"


class LocalRepositoryResponse(LocalRepository):
    """Models a local repository response."""

    enableComposerSupport: bool = False
    enableNuGetSupport: bool = False
    enableGemsSupport: bool = False
    enableNpmSupport: bool = False
    enableBowerSupport: bool = False
    enableCocoaPodsSupport: bool = False
    enableConanSupport: bool = False
    enableDebianSupport: bool = False
    enablePypiSupport: bool = False
    enablePuppetSupport: bool = False
    enableDockerSupport: bool = False
    forceNugetAuthentication: bool = False
    enableVagrantSupport: bool = False
    enableGitLfsSupport: bool = False
    enableDistRepoSupport: bool = False


class VirtualRepository(BaseRepositoryModel):
    """Models a virtual repository."""

    rclass: Literal[RClassEnum.virtual] = RClassEnum.virtual
    repositories: Optional[List[str]] = None
    artifactoryRequestsCanRetrieveRemoteArtifacts: bool = False
    debianTrivialLayout: bool = False
    keyPair: Optional[str] = None
    pomRepositoryReferencesCleanupPolicy: PomRepoRefCleanupPolicy = PomRepoRefCleanupPolicy.discard_active_reference
    defaultDeploymentRepo: Optional[str] = None
    forceMavenAuthentication: bool = False
    externalDependenciesEnabled: bool = False
    externalDependenciesPatterns: Optional[List[str]] = None
    externalDependenciesRemoteRepo: Optional[str] = None
    primaryKeyPairRef: Optional[str] = None
    secondaryKeyPairRef: Optional[str] = None


class VirtualRepositoryResponse(VirtualRepository):
    """Models a virtual repository response."""

    dockerApiVersion: str = "V2"
    enableComposerSupport: bool = False
    enableNuGetSupport: bool = False
    enableGemsSupport: bool = False
    enableNpmSupport: bool = False
    enableBowerSupport: bool = False
    enableCocoaPodsSupport: bool = False
    enableConanSupport: bool = False
    enableDebianSupport: bool = False
    enablePypiSupport: bool = False
    enablePuppetSupport: bool = False
    enableDockerSupport: bool = False
    forceNugetAuthentication: bool = False
    enableVagrantSupport: bool = False
    enableGitLfsSupport: bool = False
    enableDistRepoSupport: bool = False


class RemoteRepository(BaseRepositoryModel):
    """Models a remote Repository."""

    rclass: Literal[RClassEnum.remote] = RClassEnum.remote
    url: str
    username: Optional[str] = None
    password: Optional[SecretStr] = None
    proxy: Optional[str] = None
    remoteRepoChecksumPolicyType: str = "generate-if-absent"
    handleReleases: bool = True
    handleSnapshots: bool = True
    maxUniqueSnapshots: int = 0
    suppressPomConsistencyChecks: bool = False
    hardFail: bool = False
    offline: bool = False
    blackedOut: bool = False
    storeArtifactsLocally: bool = True
    socketTimeoutMillis: int = 15000
    localAddress: Optional[str] = None
    retrievalCachePeriodSecs: int = 43200
    failedRetrievalCachePeriodSecs: int = 30
    missedRetrievalCachePeriodSecs: int = 7200
    metadataRetrievalTimeoutSecs: int = 60
    unusedArtifactsCleanupEnabled: bool = False
    unusedArtifactsCleanupPeriodHours: int = 0
    assumedOfflinePeriodSecs: int = 300
    fetchJarsEagerly: int = False
    fetchSourcesEagerly: int = False
    shareConfiguration: bool = False
    synchronizeProperties: bool = False
    blockMismatchingMimeTypes: bool = True
    propertySets: Optional[List[str]] = None
    allowAnyHostAuth: bool = False
    enableCookieManagement: bool = False
    enableTokenAuthentication: bool = False
    bowerRegistryUrl: str = "https://registry.bower.io"
    gitRegistryUrl: str = "https://github.com/rust-lang/crates.io-index"
    composerRegistryUrl: str = "https://packagist.org"
    pyPIRegistryUrl: str = "https://pypi.org"
    vcsType: str = "GIT"
    vcsGitProvider: VcsGitProviderEnum = VcsGitProviderEnum.github
    vcsGitDownloadUrl: str = ""
    bypassHeadRequests: bool = False
    clientTlsCertificate: str = ""
    externalDependenciesEnabled: bool = False
    externalDependenciesPatterns: List[str] = ["**/*microsoft*/**", "**/*github*/**"]
    downloadRedirect: bool = False
    cdnRedirect: bool = False
    contentSynchronisation: ContentSynchronisation = ContentSynchronisation()
    feedContextPath: str = "api/v2"
    downloadContextPath: str = "api/v2/package"
    v3FeedUrl: str = "https://api.nuget.org/v3/index.json"
    blockPushingSchema1: bool = False
    priorityResolution: bool = False
    disableUrlNormalization: bool = False
    xrayIndex: bool = False
    cargoInternalIndex: bool = False


class RemoteRepositoryResponse(RemoteRepository):
    """Models a RemoteRepositoryResponse."""

    dockerApiVersion: str = "V2"
    debianTrivialLayout: bool = False
    enableComposerSupport: bool = False
    enableNuGetSupport: bool = False
    enableGemsSupport: bool = False
    enableNpmSupport: bool = False
    enableBowerSupport: bool = False
    enableCocoaPodsSupport: bool = False
    enableConanSupport: bool = False
    enableDebianSupport: bool = False
    enablePypiSupport: bool = False
    enablePuppetSupport: bool = False
    enableDockerSupport: bool = False
    forceNugetAuthentication: bool = False
    enableVagrantSupport: bool = False
    enableGitLfsSupport: bool = False
    enableDistRepoSupport: bool = False


class FederatedBaseRepostoryModel(BaseRepositoryModel):
    """
    Models a basic federated repo without members as they can't be overwritten
    and differ in response and request
    """

    rclass: Literal[RClassEnum.federated] = RClassEnum.federated
    checksumPolicyType: ChecksumPolicyType = ChecksumPolicyType.client_checksums
    handleReleases: bool = True
    handleSnapshots: bool = True
    maxUniqueSnapshots: int = 0
    maxUniqueTags: int = 0
    debianTrivialLayout: bool = False
    snapshotVersionBehavior: SnapshotVersionBehavior = SnapshotVersionBehavior.non_unique
    suppressPomConsistencyChecks: bool = False
    blackedOut: bool = False
    xrayIndex: bool = False
    propertySets: Optional[List[str]] = None
    dockerApiVersion: str = "V2"
    archiveBrowsingEnabled: bool = False
    calculateYumMetadata: bool = False
    yumRootDepth: int = 0
    enableFileListsIndexing: bool = False
    optionalIndexCompressionFormats: Optional[List[str]] = None
    downloadRedirect: bool = False
    cdnRedirect: bool = False
    blockPushingSchema1: bool = False
    primaryKeyPairRef: Optional[str] = None
    secondaryKeyPairRef: Optional[str] = None
    priorityResolution: bool = False
    cargoInternalIndex: bool = False
    terraformType: Literal["MODULE", "PROVIDER"] = "MODULE"


class FederatedRepository(FederatedBaseRepostoryModel):
    """Models a federated Repository (member model differs from reponse)."""

    members: List[FederatedMembers] = []


class FederatedRepositoryResponse(FederatedBaseRepostoryModel):
    """Models a federated repository response (member model differs from request)."""

    members: List[FederatedMembersResponse] = []
    enableComposerSupport: bool = False
    enableNuGetSupport: bool = False
    enableGemsSupport: bool = False
    enableNpmSupport: bool = False
    enableBowerSupport: bool = False
    enableCocoaPodsSupport: bool = False
    enableConanSupport: bool = False
    enableDebianSupport: bool = False
    enablePypiSupport: bool = False
    enablePuppetSupport: bool = False
    enableDockerSupport: bool = False
    forceNugetAuthentication: bool = False
    enableVagrantSupport: bool = False
    enableGitLfsSupport: bool = False
    enableDistRepoSupport: bool = False
