# Python Artifactory

`python-artifactory` is a Python library to access the [Artifactory REST API](https://www.jfrog.com/confluence/display/RTF/Artifactory+REST+API). 
This library enables you to manage Artifactory resources such as users, groups, permissions and repositories in your applications.
This library requires at least Python 3.6


## Usage

### Authentication

```
from pyartifactory import Artifactory
art = Artifactory(url="ARTIFACTORY_URL", auth=('USERNAME','PASSORD_OR_API_KEY'))
```

#### SSL Cert Verification Options
See Requests - [SSL verification](http://docs.python-requests.org/en/latest/user/advanced/#ssl-cert-verification) for more details.

Specify a local cert to use as client side certificate

```
from pyartifactory import Artifactory
art = Artifactory(url="ARTIFACTORY_URL", auth=('USERNAME','PASSORD_OR_API_KEY'), cert="/path_to_file/server.pem")
```

Disable host cert verification

```
from pyartifactory import Artifactory
art = Artifactory(url="ARTIFACTORY_URL", auth=('USERNAME','PASSORD_OR_API_KEY'), verify=False)
```

### Admin objects

#### User

First, you need to create a new Artifactory object.
```
from pyartifactory import Artifactory
art = Artifactory(url="ARTIFACTORY_URL", auth=('USERNAME','PASSORD_OR_API_KEY'))
```

Get the list of users:
```
users = art.users.list()
```

Get a single user:
```
users = art.users.get("username")
```

Create/Update a user:
```
from pyartifactory.models.User import NewUser

# Create User
user = NewUser(name="test_user", password="test_password", email="user@user.com")
new_user = art.users.create(user)

# Update user
user.email = "test@test.com"
updated_user = art.users.update(user)
```

#### Group

Get the list of groups:
```
users = art.groups.list()
```

Get a single group:
```
users = art.groups.get("group_name")
```

Create/Update a group:
```
from pyartifactory.models.Group import Group

# Create a Group
group = Group(name="test_group", description="test_group")
new_group = art.groups.create(group)

# Update user
group.description = "test_group_2"
updated_group = art.groups.update(group)
```

#### Security

A set of methods are available in the security object in order to perform operations on apiKeys, passwords ...
```python
>>> art.security.
art.security.create_api_key(          art.security.get_encrypted_password(  art.security.revoke_api_key(
art.security.get_api_key(             art.security.regenerate_api_key(      art.security.revoke_user_api_key(
```
