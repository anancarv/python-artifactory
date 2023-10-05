"""
Definition of all exceptions.
"""
from __future__ import annotations


class ArtifactoryError(Exception):
    """Generic artifactory exception."""


class UserAlreadyExistsError(ArtifactoryError):
    """User already exists."""


class GroupAlreadyExistsError(ArtifactoryError):
    """Group already exists."""


class RepositoryAlreadyExistsError(ArtifactoryError):
    """Repository already exists."""


class PermissionAlreadyExistsError(ArtifactoryError):
    """Permission already exists."""


class UserNotFoundError(ArtifactoryError):
    """The user was not found."""


class GroupNotFoundError(ArtifactoryError):
    """The group was not found."""


class RepositoryNotFoundError(ArtifactoryError):
    """The repository was not found."""


class PermissionNotFoundError(ArtifactoryError):
    """A permission object was not found."""


class ArtifactNotFoundError(ArtifactoryError):
    """An artifact was not found"""


class BadPropertiesError(ArtifactoryError):
    """Property value includes invalid characters"""


class PropertyNotFoundError(ArtifactoryError):
    """All requested properties were not found"""


class InvalidTokenDataError(ArtifactoryError):
    """The token contains invalid data."""
