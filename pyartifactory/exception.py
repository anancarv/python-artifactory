class ArtifactoryException(Exception):
    pass


class UserAlreadyExistsException(ArtifactoryException):
    pass


class GroupAlreadyExistsException(ArtifactoryException):
    pass


class RepositoryAlreadyExistsException(ArtifactoryException):
    pass


class PermissionAlreadyExistsException(ArtifactoryException):
    pass


class UserNotFoundException(ArtifactoryException):
    pass


class GroupNotFoundException(ArtifactoryException):
    pass


class RepositoryNotFoundException(ArtifactoryException):
    pass


class ArtifactNotFoundException(ArtifactoryException):
    pass


class ArtifactDeployException(ArtifactoryException):
    pass


class ArtifactDownloadException(ArtifactoryException):
    pass


class ArtifactPropertiesException(ArtifactoryException):
    pass


class ArtifactCopyException(ArtifactoryException):
    pass


class ArtifactMoveException(ArtifactoryException):
    pass


class PermissionNotFoundException(ArtifactoryException):
    pass
