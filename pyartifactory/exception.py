"""
Definition of all exceptions.
"""


class ArtifactoryException(Exception):
    """Generic artifactory exception."""


class UserAlreadyExistsException(ArtifactoryException):
    """User already exists."""


class GroupAlreadyExistsException(ArtifactoryException):
    """Group already exists."""


class RepositoryAlreadyExistsException(ArtifactoryException):
    """Repository already exists."""


class PermissionAlreadyExistsException(ArtifactoryException):
    """Permission already exists."""


class UserNotFoundException(ArtifactoryException):
    """The user was not found."""


class GroupNotFoundException(ArtifactoryException):
    """The group was not found."""


class RepositoryNotFoundException(ArtifactoryException):
    """The repository was not found."""


class PermissionNotFoundException(ArtifactoryException):
    """A permission object was not found."""


class ArtifactNotFoundException(ArtifactoryException):
    """An artifact was not found"""


class PropertyNotFoundException(ArtifactoryException):
    """All requested properties were not found"""


class InvalidTokenDataException(ArtifactoryException):
    """The token contains invalid data."""


class AqlException(ArtifactoryException):
    """AQL search failed"""
