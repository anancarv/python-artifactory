# PyArtifactory

[![Codacy Badge](https://api.codacy.com/project/badge/Grade/8b22b5118d67471f81b4de2feefc5763)](https://app.codacy.com/app/Ananias/python-artifactory?utm_source=github.com&utm_medium=referral&utm_content=anancarv/python-artifactory&utm_campaign=Badge_Grade_Dashboard)
[![Build Status](https://travis-ci.org/anancarv/python-artifactory.svg?branch=master)](https://travis-ci.org/anancarv/python-artifactory)

`pyartifactory` is a Python library to access the [Artifactory REST API](https://www.jfrog.com/confluence/display/RTF/Artifactory+REST+API). 

This library enables you to manage Artifactory resources such as users, groups, permissions, repositories & artifacts in your applications.
It requires at least Python 3.6

## Table of contents

* [Install](#Install)
* [Usage](#Usage)
    * [Authentication](#Authentication)
    * [SSL Cert Verification Options](#SSL-Cert-Verification-Options)
    * [Admin objects](#Admin-objects)
        * [User](#User)
        * [Group](#Group)
        * [Security](#Security)
        * [Repository](#Repository)
        * [Permission](#Permission)
    * [Artifacts & Builds](#Artifacts-&-Builds)
        * [Artifacts](#Artifacts)
    
## Install

```python
pip install pyartifactory 
```

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

A set of methods for performing operations on apiKeys, passwords ...
```python
>>> art.security.
art.security.create_api_key(          art.security.get_encrypted_password(  art.security.revoke_api_key(
art.security.get_api_key(             art.security.regenerate_api_key(      art.security.revoke_user_api_key(
```


### Repository

Get the list of repositories:
```python
repositories = art.repositories.list()
```

Get a single repository (Local, Virtual or Remote):
```python
local_repo = art.repositories.get_local_repo("local_repo_name")
virtual_repo = art.repositories.get_virtual_repo("virtual_repo_name")
remote_repo = art.repositories.get_remote_repo("remote_repo_name")
```

Create/Update a repository:
```python
from pyartifactory.models.Repository import LocalRepository, VirtualRepository, RemoteRepository

# Create a repository
local_repo = LocalRepository(key="test_local_repo")
new_local_repo = art.repositories.create_local_repo(local_repo)

# Update a repository
local_repo.description = "test_local_repo"
updated_local_repo = art.repositories.update_local_repo(local_repo)

# Same process for Virtual and Remote repositories
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
from pyartifactory.models.Permission import Permission

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

### Artifacts & Builds

#### Artifacts
TBD
