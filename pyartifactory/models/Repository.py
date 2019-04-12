from typing import Optional, List
from enum import Enum

from pydantic import BaseModel, SecretStr


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


class VcsGitProviderEnum(str, Enum):
    github = "GITHUB"
    bitbucket = "BITBUCKET"
    oldstash = "OLDSTASH"
    stash = "STASH"
    artifactory = "ARTIFACTORY"
    custom = "CUSTOM"


class Statistics(BaseModel):
    enabled: bool = False


class Properties(BaseModel):
    enabled: bool = False


class Source(BaseModel):
    originAbsenceDetection: bool = False


class ContentSynchronisation(BaseModel):
    enabled: bool = False
    statistics: Statistics
    properties: Properties
    source: Source


class Nuget(BaseModel):
    feedContextPath: str = "api/v2"
    downloadContextPath: str = "api/v2/package"
    v3FeedUrl: str = "https://api.nuget.org/v3/index.json"


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


class LocalRepository(BaseRepositoryModel):
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
    propertySets: List[str] = None
    dockerApiVersion: str = "V2"
    archiveBrowsingEnabled: bool = False
    calculateYumMetadata: bool = False
    yumRootDepth: int = 0
    enableFileListsIndexing: str = "false"
    optionalIndexCompressionFormats: List[str] = None
    downloadRedirect: str = "false"


class LocalRepositoryResponse(LocalRepository):
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
    repositories: List[str] = None
    artifactoryRequestsCanRetrieveRemoteArtifacts: bool = False
    debianTrivialLayout: bool = False
    keyPair: Optional[str] = None
    pomRepositoryReferencesCleanupPolicy: PomRepoRefCleanupPolicy = PomRepoRefCleanupPolicy.discard_active_reference
    defaultDeploymentRepo: Optional[str] = None
    forceMavenAuthentication: bool = False
    externalDependenciesEnabled: bool = False
    externalDependenciesPatterns: List[str] = None
    externalDependenciesRemoteRepo: str = None


class VirtualRepositoryResponse(LocalRepository):
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
    url: str
    username: str = None
    password: SecretStr = None
    proxy: str = None
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
    localAddress: str = None
    retrievalCachePeriodSecs: int = 43200
    failedRetrievalCachePeriodSecs: int = 30
    missedRetrievalCachePeriodSecs: int = 7200
    unusedArtifactsCleanupEnabled: bool = False
    unusedArtifactsCleanupPeriodHours: int = 0
    assumedOfflinePeriodSecs: int = 300
    fetchJarsEagerly: int = False
    fetchSourcesEagerly: int = False
    shareConfiguration: bool = False
    synchronizeProperties: bool = False
    blockMismatchingMimeTypes: bool = True
    propertySets: List[str] = None
    allowAnyHostAuth: bool = False
    enableCookieManagement: bool = False
    bowerRegistryUrl: str = "https://registry.bower.io"
    composerRegistryUrl: str = "https://packagist.org"
    pyPIRegistryUrl: str = "https://pypi.org"
    vcsType: str = "GIT"
    vcsGitProvider: VcsGitProviderEnum = VcsGitProviderEnum.github
    vcsGitDownloadUrl: str = ""
    bypassHeadRequest: bool = False
    clientTlsCertificate: str = ""
    externalDependenciesEnabled: bool = False
    externalDependenciesPatterns: List[str] = ["**/*microsoft*/**", "**/*github*/**"]
    downloadRedirect: bool = False
    contentSynchronisation: ContentSynchronisation
    nuget: Nuget


class RemoteRepositoryResponse(RemoteRepository):
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
