"Artifactory queries"
from typing import List, Dict, Optional, Union, Any
from enum import Enum

from pydantic import BaseModel


class SortTypesEnum(str, Enum):
    "Order of query results"
    asc = "$asc"
    desc = "$desc"


class DomainQueryEnum(str, Enum):
    "Artifactory domain objects to be queried"
    items = "items"
    builds = "builds"
    entries = "entries"


class Aql(BaseModel):
    "Artifactory Query Language"
    domain: DomainQueryEnum = DomainQueryEnum.items
    find: Optional[Dict[str, Union[str, List[Dict[str, Any]], Dict[str, str]]]]
    include: Optional[List[str]]
    sort: Optional[Dict[SortTypesEnum, List[str]]] = None
    offset: Optional[int] = None
    limit: Optional[int] = None
