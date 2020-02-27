"""
Definition of all Aql models.
"""

from typing import List, Dict, Optional, Union, Any
from enum import Enum
from pydantic import BaseModel


class SortTypesEnum(str, Enum):
    """Models a sort type."""

    asc = "$asc"
    desc = "$desc"


class DomainQueryEnum(str, Enum):
    """Models a domain query."""

    items = "items"
    builds = "builds"
    entries = "entries"


class Aql(BaseModel):
    """Models an Aql query."""

    domain: DomainQueryEnum = DomainQueryEnum.items
    find: Optional[Dict[str, Union[str, List[Dict[str, Any]], Dict[str, str]]]]
    include: Optional[List[str]]
    sort: Optional[Dict[SortTypesEnum, List[str]]] = None
    offset: Optional[int] = None
    limit: Optional[int] = None
