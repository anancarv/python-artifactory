# PyArtifactory

[![GitHub Actions workflow](https://github.com/anancarv/python-artifactory/workflows/Check%20code/badge.svg)](https://github.com/anancarv/python-artifactory/actions)
[![PyPI version](https://badge.fury.io/py/pyartifactory.svg)](https://badge.fury.io/py/pyartifactory)
[![Codacy Badge](https://api.codacy.com/project/badge/Grade/8b22b5118d67471f81b4de2feefc5763)](https://app.codacy.com/app/Ananias/python-artifactory?utm_source=github.com&utm_medium=referral&utm_content=anancarv/python-artifactory&utm_campaign=Badge_Grade_Dashboard)
[![Codacy Badge](https://api.codacy.com/project/badge/Coverage/b4a37e92d42d4815938dd77a7099dfd1)](https://www.codacy.com/manual/Ananias/python-artifactory?utm_source=github.com&utm_medium=referral&utm_content=anancarv/python-artifactory&utm_campaign=Badge_Coverage)
![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)


`pyartifactory` is a Python library to access the [Artifactory REST API](https://www.jfrog.com/confluence/display/RTF/Artifactory+REST+API). 

This library enables you to manage Artifactory resources such as users, groups, permissions, repositories, artifacts and access tokens in your applications. Based on Python 3.6+ type hints.

<!-- toc -->

- [Requirements](#requirements)
- [Install](#install)
- [Usage](#usage)
  * [Authentication](#authentication)
  * [SSL Cert Verification Options](#ssl-cert-verification-options)
  * [Admin objects](#admin-objects)
    + [User](#user)
    + [Group](#group)
    + [Security](#security)
    + [Repository](#repository)
    + [Permission](#permission)
  * [Artifacts](#artifacts)
    + [Deploy an artifact](#deploy-an-artifact)
    + [Download an artifact](#download-an-artifact)
    + [Retrieve artifact properties](#retrieve-artifact-properties)
    + [Retrieve artifact stats](#retrieve-artifact-stats)
    + [Copy artifact to a new location](#copy-artifact-to-a-new-location)
    + [Move artifact to a new location](#move-artifact-to-a-new-location)
    + [Delete an artifact](#delete-an-artifact)
  * [Contributing](#contributing)

<!-- tocstop -->

## Requirements

* Python 3.6+


## Install

```python
pip install pyartifactory 
```

## Usage

### Authentication

```python
from pyartifactory import Artifactory
art = Artifactory(url="ARTIFACTORY_URL", auth=('USERNAME','PASSWORD_OR_API_KEY'))
```

### SSL Cert Verification Options
Specify a local cert to use as client side certificate

```python
from pyartifactory import Artifactory
art = Artifactory(url="ARTIFACTORY_URL", auth=('USERNAME','PASSORD_OR_API_KEY'), cert="/path_to_file/server.pem")
```

Disable host cert verification

```python
from pyartifactory import Artifactory
art = Artifactory(url="ARTIFACTORY_URL", auth=('USERNAME','PASSORD_OR_API_KEY'), verify=False)
```

### Admin objects

#### User

First, you need to create a new Artifactory object.
```python
from pyartifactory import Artifactory
art = Artifactory(url="ARTIFACTORY_URL", auth=('USERNAME','PASSORD_OR_API_KEY'))
```

Get the list of users:
```python
users = art.users.list()
```

Get a single user:
```python
user = art.users.get("test_user")
```

Create a user:
```python
from pyartifactory.models import NewUser

# Create User
user = NewUser(name="test_user", password="test_password", email="user@user.com")
new_user = art.users.create(user)

# Update user
user.email = "test@test.com"
updated_user = art.users.update(user)
```

Update a user:
```python
from pyartifactory.models import User

user = art.users.get("test_user")

# Update user
user.email = "test@test.com"
updated_user = art.users.update(user)
```

Delete a user:
```python
art.users.delete("test_user")
```

Unlock a user:
```python
art.users.unlock("test_user")
```

#### Group

Get the list of groups:
```python
users = art.groups.list()
```

Get a single group:
```python
users = art.groups.get("group_name")
```

Create/Update a group:
```python
from pyartifactory.models import Group

# Create a Group
group = Group(name="test_group", description="test_group")
new_group = art.groups.create(group)

# Update user
group.description = "test_group_2"
updated_group = art.groups.update(group)
```

Delete a group:
```python
art.groups.delete("test_group")
```

#### Security

A set of methods for performing operations on apiKeys, passwords ...
```python
>>> art.security.
art.security.create_api_key(          art.security.get_encrypted_password(  art.security.revoke_api_key(
art.security.get_api_key(             art.security.regenerate_api_key(      art.security.revoke_user_api_key(
```

Create an access token (for a transient user):
```python
token = art.security.create_access_token(user_name='transient_artifactory_user', 
                                         groups=['g1', 'g2'],
                                         refreshable=True)
```

Create an access token for an existing user (groups are implied from the existing user):
```python
token = art.security.create_access_token(user_name='existing_artifactory_user', 
                                         refreshable=True)
```

Revoke an existing revocable token:
```python
art.security.revoke_access_token(token.access_token)
```

#### Repository

Get the list of repositories:
```python
repositories = art.repositories.list()
```

Get a single repository
```python
repo = art.repositories.get_repo("repo_name")
# According to the repo type, you'll have either a local, virtual or remote repository returned
```

Create/Update a repository:
```python
from pyartifactory.models import LocalRepository, VirtualRepository, RemoteRepository

# Create local repo
local_repo = LocalRepository(key="test_local_repo")
new_local_repo = art.repositories.create_repo(local_repo)

# Create virtual repo
virtual_repo = VirtualRepository(key="test_virtual_repo")
new_virtual_repo = art.repositories.create_repo(virtual_repo)

# Create remote repo
remote_repo = RemoteRepository(key="test_remote_repo")
new_remote_repo = art.repositories.create_repo(remote_repo)

# Update a repository
local_repo = art.repositories.get_repo("test_local_repo")
local_repo.description = "test_local_repo"
updated_local_repo = art.repositories.update_repo(local_repo)
```

Delete a repository:
```python
art.repositories.delete("test_local_repo")
```

#### Permission
Get the list of permissions:
```python
permissions = art.permissions.list()
```

Get a single permission:
```python
users = art.permissions.get("test_permission")
```

Create/Update a permission:
```python
from pyartifactory.models import Permission

# Create a permission
permission = Permission(
    **{
        "name": "test_permission",
        "repositories": ["test_repository"],
        "principals": {
            "users": {"test_user": ["r", "w", "n", "d"]},
            "groups": {"developers": ["r"]},
        },
    }
)
perm = art.permissions.create(permission)

# Update permission
permission.repositories = ["test_repository_2"]
updated_permission = art.permissions.update(permission)
```

Delete a permission:
```python
art.permissions.delete("test_permission")
```

### Artifacts

#### Deploy an artifact
```python
artifact = art.artifacts.deploy("<LOCAL_FILE_LOCATION>", "<ARTIFACT_PATH_IN_ARTIFACTORY>")
# artifact = art.artifacts.deploy("Desktop/myNewFile.txt", "my-repository/my/new/artifact/directory/file.txt")
```

#### Download an artifact
```python
artifact = art.artifacts.download("<ARTIFACT_PATH_IN_ARTIFACTORY>", "<LOCAL_DIRECTORY_PATH>")
# artifact = art.artifacts.download("my-artifactory-repository/my/new/artifact/file.txt", "Desktop/my/local/directory")
# The artifact location is returned by the download method
# If you have not set a <LOCAL_DIRECTORY_PATH>, the artifact will be downloaded in the current directory
```

#### Retrieve artifact properties
```python
artifact_properties = art.artifacts.properties("<ARTIFACT_PATH_IN_ARTIFACTORY>")
# artifact_properties = art.artifacts.properties("my-repository/my/new/artifact/directory/file.txt")
>>> print(artifact_properties.json)
```

#### Retrieve artifact stats
```python
artifact_stats = art.artifacts.stats("<ARTIFACT_PATH_IN_ARTIFACTORY>")
# artifact_stats = art.artifacts.stats("my-repository/my/new/artifact/directory/file.txt")
>>> print(artifact_stats.json)
```

#### Copy artifact to a new location
```python
artifact = art.artifacts.copy("<CURRENT_ARTIFACT_PATH_IN_ARTIFACTORY>","<NEW_ARTIFACT_PATH_IN_ARTIFACTORY>")

# If you want to run a dryRun test, you can do the following:
# artifact = art.artifacts.copy("my-repository/current/artifact/path/file.txt","my-repository/new/artifact/path/file.txt", dryrun=True)
# It will return properties of the newly copied artifact
```

#### Move artifact to a new location
```python
artifact = art.artifacts.move("<CURRENT_ARTIFACT_PATH_IN_ARTIFACTORY>","<NEW_ARTIFACT_PATH_IN_ARTIFACTORY>")

# You can also run a dryRun test with the move operation
# It will return properties of the newly moved artifact
```

#### Delete an artifact
```python
art.artifacts.delete("<ARTIFACT_PATH_IN_ARTIFACTORY>")
```


### Contributing
Please read the [Development - Contributing](./CONTRIBUTING.md) guidelines.
