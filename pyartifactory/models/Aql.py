from pydantic import BaseModel
from typing import List, Dict, Optional, Union, Any
from enum import Enum


class SortTypesEnum(str, Enum):
    asc = "$asc"
    desc = "$desc"


class DomainQueryEnum(str, Enum):
    items = "items"
    builds = "builds"
    entries = "entries"


class Aql(BaseModel):
    domain: DomainQueryEnum = DomainQueryEnum.items
    find: Optional[Dict[str, Union[str, List[Dict[str, Any]], Dict[str, str]]]]
    include: Optional[List[str]]
    sort: Optional[Dict[SortTypesEnum, List[str]]] = None
    offset: Optional[int] = None
    limit: Optional[int] = None
