# PyArtifactory

[![GitHub Actions workflow](https://github.com/anancarv/python-artifactory/workflows/Check%20code/badge.svg)](https://github.com/anancarv/python-artifactory/actions)
[![PyPI version](https://badge.fury.io/py/pyartifactory.svg)](https://badge.fury.io/py/pyartifactory)
[![Codacy Badge](https://app.codacy.com/project/badge/Grade/c02851e5b9f24fe299783b48eab18f54)](https://www.codacy.com/gh/anancarv/python-artifactory/dashboard?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=anancarv/python-artifactory&amp;utm_campaign=Badge_Grade)
[![Codacy Badge](https://app.codacy.com/project/badge/Coverage/c02851e5b9f24fe299783b48eab18f54)](https://www.codacy.com/gh/anancarv/python-artifactory/dashboard?utm_source=github.com&utm_medium=referral&utm_content=anancarv/python-artifactory&utm_campaign=Badge_Coverage)
![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)


`pyartifactory` is a Python library to access the [Artifactory REST API](https://www.jfrog.com/confluence/display/RTF/Artifactory+REST+API).

This library enables you to manage Artifactory resources such as users, groups, permissions, repositories, artifacts and access tokens in your applications. Based on Python 3.8+ type hints.

<!-- toc -->

- [Requirements](#requirements)
- [Install](#install)
- [Usage](#usage)
  * [Authentication](#authentication)
    + [Basic authentication](#basic-authentication)
    + [Authentication with access token](#authentication-with-access-token)
  * [SSL Cert Verification Options](#ssl-cert-verification-options)
  * [Timeout option](#timeout-option)
  * [Admin objects](#admin-objects)
    + [User](#user)
    + [Group](#group)
    + [Security](#security)
    + [Repository](#repository)
    + [Permission](#permission)
      - [Artifactory lower than 6.6.0](#artifactory-lower-than-660)
      - [Artifactory 6.6.0 or higher](#artifactory-660-or-higher)
  * [Artifacts](#artifacts)
    + [Get the information about a file or folder](#get-the-information-about-a-file-or-folder)
    + [Deploy an artifact](#deploy-an-artifact)
    + [Deploy an artifact with properties](#deploy-an-artifact-with-properties)
    + [Deploy an artifact with checksums](#deploy-an-artifact-with-checksums)
    + [Download an artifact](#download-an-artifact)
    + [Retrieve artifact list](#retrieve-artifact-list)
    + [Retrieve artifact properties](#retrieve-artifact-properties)
    + [Set artifact properties](#set-artifact-properties)
    + [Update artifact properties](#update-artifact-properties)
    + [Retrieve artifact stats](#retrieve-artifact-stats)
    + [Copy artifact to a new location](#copy-artifact-to-a-new-location)
    + [Move artifact to a new location](#move-artifact-to-a-new-location)
    + [Delete an artifact](#delete-an-artifact)
  * [Builds](#builds)
    + [Get a list of all builds](#get-a-list-of-all-builds)
    + [Get the information about a build](#get-the-information-about-a-build)
    + [Create build](#create-build)
    + [Promote a build](#promote-a-build)
    + [Delete one or more builds](#delete-one-or-more-builds)
    + [Rename a build](#rename-a-build)
    + [Get differences between two builds](#get-differences-between-two-builds)
  * [Contributing](#contributing)

<!-- tocstop -->

## Requirements

- Python 3.8+

## Install

```python
pip install pyartifactory
```

## Usage

### Authentication

Since Artifactory 6.6.0 there is version 2 of the REST API for permission management, in case you have that version or higher, you need to pass api_version=2 to the constructor when you instantiate the class.

#### Basic authentication
```python
from pyartifactory import Artifactory
art = Artifactory(url="ARTIFACTORY_URL", auth=('USERNAME','PASSWORD_OR_API_KEY'), api_version=1)
```

#### Authentication with access token
```python
from pyartifactory import Artifactory
art = Artifactory(url="ARTIFACTORY_URL", access_token="your-access-token")
```

Note:
* If you set both `access_token` and `auth`, the access_token authentication will be chosen
* If you do not set any authentication method, API calls will be done without authentication (anonymous)

### SSL Cert Verification Options

Specify a local cert to use as client side certificate

```python
from pyartifactory import Artifactory
art = Artifactory(url="ARTIFACTORY_URL", auth=('USERNAME','PASSWORD_OR_API_KEY'), cert="/path_to_file/server.pem", api_version=1)
```

Specify a local cert to use as custom CA certificate

```python
from pyartifactory import Artifactory
art = Artifactory(url="ARTIFACTORY_URL", auth=('USERNAME','PASSWORD_OR_API_KEY'), verify="/path_to_file/ca.pem", cert="/path_to_file/server.pem", api_version=1)
```

> `verify` and `cert` configure certificates for distinct purposes. `verify` determines SSL/TLS certificate validation for the server, while `cert` supplies a client certificate for mutual authentication, as required by the server. You can use either one or both parameters as needed.

Disable host cert verification

```python
from pyartifactory import Artifactory
art = Artifactory(url="ARTIFACTORY_URL", auth=('USERNAME','PASSWORD_OR_API_KEY'), verify=False, api_version=1)
```

> `verify` can be also set as a boolean to enable/disable SSL host verification.

### Timeout option

Use timeout option to limit connect and read timeout in case the artifactory server is not responding in a timely manner.

```python
from pyartifactory import Artifactory
art = Artifactory(url="ARTIFACTORY_URL", auth=('USERNAME','PASSWORD_OR_API_KEY'), api_version=1, timeout=60)
```

> `timeout` is None by default.

### Admin objects

#### User

First, you need to create a new Artifactory object.
```python
from pyartifactory import Artifactory
art = Artifactory(url="ARTIFACTORY_URL", auth=('USERNAME','PASSWORD_OR_API_KEY'))
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
groups = art.groups.list()
```

Get a single group:
```python
group = art.groups.get("group_name")
```

Create/Update a group:
```python
from pyartifactory.models import Group

# Create a Group
group = Group(name="test_group", description="test_group")
new_group = art.groups.create(group)

# Update a Group
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

Create an access token:
```python
token = art.security.create_access_token(user_name='artifactory_user', refreshable=True, scope="applied-permissions/user")
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
from pyartifactory.models import (
    LocalRepository,
    VirtualRepository,
    RemoteRepository,
    FederatedRepository
)

# Create local repo
local_repo = LocalRepository(key="test_local_repo")
new_local_repo = art.repositories.create_repo(local_repo)

# Create virtual repo
virtual_repo = VirtualRepository(key="test_virtual_repo")
new_virtual_repo = art.repositories.create_repo(virtual_repo)

# Create remote repo
remote_repo = RemoteRepository(key="test_remote_repo", url="http://test-url.com")
new_remote_repo = art.repositories.create_repo(remote_repo)

# Create federated repo
remote_repo = FederatedRepository(key="test_remote_repo")
new_federated_repo = art.repositories.create_repo(remote_repo)

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

##### Artifactory lower than 6.6.0

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

##### Artifactory 6.6.0 or higher
```python
from pyartifactory import Artifactory
from pyartifactory.models import PermissionV2
from pyartifactory.models.permission import PermissionEnumV2, PrincipalsPermissionV2, RepoV2, BuildV2, ReleaseBundleV2

# To use PermissionV2, make sure to set api_version=2
art = Artifactory(url="ARTIFACTORY_URL", auth=('USERNAME','PASSWORD_OR_API_KEY'), api_version=2)

# Create a permission
permission = PermissionV2(
    name="test_permission",
    repo=RepoV2(
        repositories=["test_repository"],
        actions=PrincipalsPermissionV2(
            users={
                "test_user": [
                    PermissionEnumV2.read,
                    PermissionEnumV2.annotate,
                    PermissionEnumV2.write,
                    PermissionEnumV2.delete,
                ]
            },
            groups={
                "developers": [
                    PermissionEnumV2.read,
                    PermissionEnumV2.annotate,
                    PermissionEnumV2.write,
                    PermissionEnumV2.delete,
                ],
            },
        ),
        includePatterns=["**"],
        excludePatterns=[],
    ),
    build=BuildV2(
          actions=PrincipalsPermissionV2(
              users={
                  "test_user": [
                      PermissionEnumV2.read,
                      PermissionEnumV2.write,
                  ]
              },
              groups={
                  "developers": [
                      PermissionEnumV2.read,
                      PermissionEnumV2.write,
                  ],
              },
          ),
          includePatterns=[""],
          excludePatterns=[""],
      ),
    releaseBundle=ReleaseBundleV2(
          repositories=["release-bundles"],
          actions=PrincipalsPermissionV2(
              users={
                  "test_user": [
                      PermissionEnumV2.read,
                  ]
              },
              groups={
                  "developers": [
                      PermissionEnumV2.read,
                  ],
              },
          ),
          includePatterns=[""],
          excludePatterns=[""],
      )
  # You don't have to set all the objects repo, build and releaseBundle
  # If you only need repo for example, you can set only the repo object
)
perm = art.permissions.create(permission)

# Update permission
permission.repo.repositories = ["test_repository_2"]
updated_permission = art.permissions.update(permission)
```

Delete a permission:
```python
art.permissions.delete("test_permission")
```

### Artifacts

#### Get the information about a file or folder
```python
artifact_info = art.artifacts.info("<ARTIFACT_PATH_IN_ARTIFACTORY>")
# file_info = art.artifacts.info("my-repository/my/artifact/directory/file.txt")
# folder_info = art.artifacts.info("my-repository/my/artifact/directory")
```

#### Deploy an artifact

```python
artifact = art.artifacts.deploy("<LOCAL_FILE_LOCATION>", "<ARTIFACT_PATH_IN_ARTIFACTORY>")
# artifact = art.artifacts.deploy("Desktop/myNewFile.txt", "my-repository/my/new/artifact/directory/file.txt")
```

#### Deploy an artifact with properties

```python
artifact = art.artifacts.deploy("<LOCAL_FILE_LOCATION>", "<ARTIFACT_PATH_IN_ARTIFACTORY>", "<PROPERTIES>")
# artifact = art.artifacts.deploy("Desktop/myNewFile.txt", "my-repository/my/new/artifact/directory/file.txt", {"retention": ["30"]})
```

#### Deploy an artifact with checksums

```python
artifact = art.artifacts.deploy("<LOCAL_FILE_LOCATION>", "<ARTIFACT_PATH_IN_ARTIFACTORY>", checksum_enabled=True)
# artifact = art.artifacts.deploy("Desktop/myNewFile.txt", "my-repository/my/new/artifact/directory/file.txt", checksums=True)
```
Deploy an artifact to the specified destination by checking if the artifact content already exists in Artifactory.

If Artifactory already contains a user-readable artifact with the same checksum the artifact content is copied over
to the new location and returns a response without requiring content transfer.

Otherwise, a 404 error is returned to indicate that content upload is expected in order to deploy the artifact.

**Note**: The performance might suffer when deploying artifacts with checksums enabled.

#### Download an artifact
```python
artifact = art.artifacts.download("<ARTIFACT_PATH_IN_ARTIFACTORY>", "<LOCAL_DIRECTORY_PATH>")
# artifact = art.artifacts.download("my-artifactory-repository/my/new/artifact/file.txt", "Desktop/my/local/directory")
# The artifact location is returned by the download method
# If you have not set a <LOCAL_DIRECTORY_PATH>, the artifact will be downloaded in the current directory
```

#### Retrieve artifact list
```python
artifacts = art.artifacts.list("<ARTIFACT_PATH_IN_ARTIFACTORY>")
# files_only = art.artifacts.list("<ARTIFACT_PATH_IN_ARTIFACTORY>", list_folders=False)
# non_recursive = art.artifacts.list("<ARTIFACT_PATH_IN_ARTIFACTORY>", recursive=False)
# max_depth = art.artifacts.list("<ARTIFACT_PATH_IN_ARTIFACTORY>", depth=3)
```

#### Retrieve artifact properties
```python
artifact_properties = art.artifacts.properties("<ARTIFACT_PATH_IN_ARTIFACTORY>")  # returns all properties
# artifact_properties = art.artifacts.properties("my-repository/my/new/artifact/directory/file.txt")
artifact_properties = art.artifacts.properties("<ARTIFACT_PATH_IN_ARTIFACTORY>", ["prop1", "prop2"])  # returns specific properties
artifact_properties.properties["prop1"]  # ["value1", "value1-bis"]
```

#### Set artifact properties
```python
artifact_properties = art.artifacts.set_properties("<ARTIFACT_PATH_IN_ARTIFACTORY>", {"prop1": ["value"], "prop2": ["value1", "value2", "etc"})  # recursive mode is enabled by default
artifact_properties = art.artifacts.set_properties("<ARTIFACT_PATH_IN_ARTIFACTORY>", {"prop1": ["value"], "prop2": ["value1", "value2", "etc"]}, False) # disable recursive mode
```

#### Update artifact properties
```python
artifact_properties = art.artifacts.update_properties("<ARTIFACT_PATH_IN_ARTIFACTORY>", {"prop1": ["value"], "prop2": ["value1", "value2", "etc"})  # recursive mode is enabled by default
artifact_properties = art.artifacts.update_properties("<ARTIFACT_PATH_IN_ARTIFACTORY>", {"prop1": ["value"], "prop2": ["value1", "value2", "etc"}, False) # disable recursive mode
```

#### Retrieve artifact stats
```python
artifact_stats = art.artifacts.stats("<ARTIFACT_PATH_IN_ARTIFACTORY>")
# artifact_stats = art.artifacts.stats("my-repository/my/new/artifact/directory/file.txt")
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



### Builds

#### Get a list of all builds
```python
build_list: BuildListResponse = art.builds.list()
```

#### Get the information about a build

```python
build_info: BuildInfo = art.builds.get_build_info("<build_name>", "<build_number>")
```

Note: optional BuildProperties can be used to query the correct build info of interest.

```python
build_properties = BuildProperties(diff="<older_build>")
build_info: BuildInfo = art.builds.get_build_info("<build_name>", "<build_number>", properties=build_properties)
# build_info contains diff between <build_number> and <older_build>
```


```python
# started is the earliest build time to return
build_properties = BuildProperties(started="<yyyy-MM-dd'T'HH:mm:ss.SSSZ>")
build_info: BuildInfo = art.builds.get_build_info("<build_name>", "<build_number>", properties=build_properties)
```

#### Create build

```python
build_create_request = BuildCreateRequest(name="<build_name>", number="<build_number>", started="<Build start time in the format of yyyy-MM-dd'T'HH:mm:ss.SSSZ>")
create_build = art.builds.create_build(build_create_request)
```


#### Promote a build
```python
build_promote_request = BuildPromotionRequest(sourceRepo="<source-jfrog-repo>", targetRepo="<target-jfrog-repo>")
promote_build: BuildPromotionResult = art.builds.promote_build("<build_name>", "<build_number>", build_promote_request)
```

#### Delete one or more builds
```python
build_delete_request = BuildDeleteRequest(buildName="<build_name>", buildNumbers=["<build_number>", "<another_build_number>", ...])
art.builds.delete(build_delete_request)
```

#### Rename a build
```python
art.builds.build_rename("<build_name>", "<new_build_name>")
```

#### Get differences between two builds
```python
build_diffs: BuildDiffResponse = art.builds.build_diff("<build_name>", "<build_number>", "<older_build_number>")
```


### Contributing
Please read the [Development - Contributing](./CONTRIBUTING.md) guidelines.
