"""
Import all object definitions here and name the package logger.
"""
import logging

from pyartifactory.objects import (
    ArtifactoryUser,
    ArtifactoryGroup,
    ArtifactorySecurity,
    ArtifactoryRepository,
    ArtifactoryArtifact,
    ArtifactoryPermission,
    Artifactory,
    AccessTokenModel,
)

__version__ = "1.4.0"

logging.getLogger(__name__)
