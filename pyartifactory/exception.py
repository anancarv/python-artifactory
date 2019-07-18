class UserAlreadyExistsException(Exception):
    pass


class GroupAlreadyExistsException(Exception):
    pass


class RepositoryAlreadyExistsException(Exception):
    pass


class PermissionAlreadyExistsException(Exception):
    pass


class UserNotFoundException(Exception):
    pass


class GroupNotFoundException(Exception):
    pass


class RepositoryNotFoundException(Exception):
    pass


class PermissionNotFoundException(Exception):
    pass
