from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, EmailStr, SecretStr, HttpUrl


class SimpleUser(BaseModel):
    name: str
    uri: HttpUrl
    realm: Optional[str] = None


class BaseUserModel(BaseModel):
    name: str
    admin: Optional[bool] = False
    profileUpdatable: Optional[bool] = True
    disableUIAccess: Optional[bool] = False
    internalPasswordDisabled: Optional[bool] = False
    groups: Optional[List[str]] = None


class NewUser(BaseUserModel):
    email: EmailStr
    password: SecretStr


class User(BaseUserModel):
    email: Optional[EmailStr] = None


class UserResponse(BaseUserModel):
    email: EmailStr
    lastLoggedIn: Optional[datetime] = None
    realm: Optional[str] = None
    offlineMode: bool = False
