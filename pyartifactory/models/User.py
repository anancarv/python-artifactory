from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, EmailStr, SecretStr


class SimpleUser(BaseModel):
    name: str
    uri: str
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


class UserResponse(BaseUserModel):
    email: EmailStr
    lastLoggedIn: Optional[datetime] = None
    realm: Optional[str] = None
    offlineMode: bool = False
