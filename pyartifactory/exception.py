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


class PermissionNotFoundException(ArtifactoryException):
    pass
