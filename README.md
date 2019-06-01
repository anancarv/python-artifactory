# Python Artifactory

[![Codacy Badge](https://api.codacy.com/project/badge/Grade/8b22b5118d67471f81b4de2feefc5763)](https://app.codacy.com/app/Ananias/python-artifactory?utm_source=github.com&utm_medium=referral&utm_content=anancarv/python-artifactory&utm_campaign=Badge_Grade_Dashboard)
[![Build Status](https://travis-ci.org/anancarv/python-artifactory.svg?branch=master)](https://travis-ci.org/anancarv/python-artifactory)

`python-artifactory` is a Python library to access the [Artifactory REST API](https://www.jfrog.com/confluence/display/RTF/Artifactory+REST+API). 
This library enables you to manage Artifactory resources such as users, groups, permissions, repositories & artifacts in your applications.
This library requires at least Python 3.6

## Table of contents


* [Usage](#Usage)
* [Authentication](#Authentication)
* [SSL Cert Verification Options](#SSL-Cert-Verification-Options)
* [Admin objects](#Admin-objects)
  * [User](#Users)
  * [Group](#Groups)
  * [Security](#Security)
  * [Repository](#Repositories)
  * [Permission](#Permissions)
* [Artifacts & Builds](#Artifacts-&-Builds)
  * [Artifacts](#Artifacts)
  * [Builds](#Builds)
    
    
## Usage

### Authentication

```python
from pyartifactory import Artifactory
art = Artifactory(url="ARTIFACTORY_URL", auth=('USERNAME','PASSORD_OR_API_KEY'))
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

#### Users

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
users = art.users.get("test_user")
```

Create/Update a user:
```python
from pyartifactory.models.User import NewUser

# Create User
user = NewUser(name="test_user", password="test_password", email="user@user.com")
new_user = art.users.create(user)

# Update user
user.email = "test@test.com"
updated_user = art.users.update(user)
```

Delete a user:
```python
art.users.delete("test_user")
```

#### Groups

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
from pyartifactory.models.Group import Group

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

A set of methods are available in the security object in order to perform operations on apiKeys, passwords ...
```python
>>> art.security.
art.security.create_api_key(          art.security.get_encrypted_password(  art.security.revoke_api_key(
art.security.get_api_key(             art.security.regenerate_api_key(      art.security.revoke_user_api_key(
```

#### Repositories

Get the list of repositories:
```python
repositories = art.repositories.list()
```

Get a single repository (Local, Virtual or Remote):
```python
local_repo = art.groups.get_local_repo("local_repo_name")
virtual_repo = art.groups.get_virtual_repo("virtual_repo_name")
remote_repo = art.groups.get_remote_repo("remote_repo_name")
```

Create/Update a repository:
```python
from pyartifactory.models.Repository import LocalRepository, VirtualRepository, RemoteRepository

# Create a repository
local_repo = LocalRepository(key="test_local_repo")
new_local_repo = art.repositories.create_local_repo(local_repo)

# Update repository
local_repo.description = "test_local_repo"
updated_local_repo = art.repositories.update_local_repo(local_repo)

# Same process for Virtual and Remote repositories
```

Delete a repository:
```python
art.repositories.delete("test_local_repo")
```


#### Permissions
TBD


### Artifacts & Builds

#### Artifacts
Deploy an artifact:
```python
artifact = art.artifacts.deploy("<ARTIFACT_PATH_IN_ARTIFACTORY>","<LOCAL_FILE_LOCATION>")
# artifact = art.artifacts.deploy("my-repository/my/new/artifact/directory/file.txt","Desktop/myNewFile.txt")
```


Download an artifact (The artifact will be downloaded in the current directory):
```python
artifact = art.artifacts.download("<ARTIFACT_PATH_IN_ARTIFACTORY>")
# artifact = art.artifacts.download("my-repository/my/new/artifact/directory/file.txt")
```

Retrieve artifact properties:
```python
artifact_properties = art.artifacts.properties("<ARTIFACT_PATH_IN_ARTIFACTORY>")
# artifact_properties = art.artifacts.properties("my-repository/my/new/artifact/directory/file.txt")
>>> print(artifact_properties.json)
```

Retrieve artifact stats:
```python
artifact_stats = art.artifacts.stats("<ARTIFACT_PATH_IN_ARTIFACTORY>")
# artifact_stats = art.artifacts.stats("my-repository/my/new/artifact/directory/file.txt")
>>> print(artifact_stats.json)
```

Copy artifact to a new location:
```python
artifact = art.artifacts.copy("<CURRENT_ARTIFACT_PATH_IN_ARTIFACTORY>","<NEW_ARTIFACT_PATH_IN_ARTIFACTORY>")

# If you want to run a dryRun test, you can do the following:
# artifact = art.artifacts.copy("<CURRENT_ARTIFACT_PATH_IN_ARTIFACTORY>","<NEW_ARTIFACT_PATH_IN_ARTIFACTORY>", dryrun=True)

```

Move artifact to a new location:
```python
artifact = art.artifacts.move("<CURRENT_ARTIFACT_PATH_IN_ARTIFACTORY>","<NEW_ARTIFACT_PATH_IN_ARTIFACTORY>")

# You can also run a dryRun test with the move operation
```

Delete an artifact:
```python
art.artifacts.delete("<ARTIFACT_PATH_IN_ARTIFACTORY>")
```

#### Builds
TBD
