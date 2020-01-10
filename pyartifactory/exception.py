class ArtifactoryException(Exception):
    """Generic artifactory exception."""
    pass


class UserAlreadyExistsException(ArtifactoryException):
    """User already exists."""
    pass


class GroupAlreadyExistsException(ArtifactoryException):
    """Group already exists."""
    pass


class RepositoryAlreadyExistsException(ArtifactoryException):
    """Repository already exists."""
    pass


class PermissionAlreadyExistsException(ArtifactoryException):
    """Permission already exists."""
    pass


class UserNotFoundException(ArtifactoryException):
    """The user was not found."""
    pass


class GroupNotFoundException(ArtifactoryException):
    """The group was not found."""
    pass


class RepositoryNotFoundException(ArtifactoryException):
    """The repository was not found."""
    pass


class PermissionNotFoundException(ArtifactoryException):
    """A permission object was not found."""
    pass
