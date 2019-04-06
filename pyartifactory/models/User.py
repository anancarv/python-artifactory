from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, EmailStr, SecretStr


class BaseUserModel(BaseModel):
    name: str
    admin: Optional[bool] = None
    profileUpdatable: Optional[bool] = None
    disableUIAccess: Optional[bool] = None
    internalPasswordDisabled: Optional[bool] = None
    groups: Optional[List[str]] = None


class NewUser(BaseUserModel):
    email: EmailStr
    password: SecretStr


class User(BaseUserModel):
    email: EmailStr
    lastLoggedIn: datetime = None
    realm: str = None


class UserList(BaseModel):
    users: List[BaseUserModel] = None
