"""
Definition of all utils.
"""

from typing import Any

from pydantic import SecretStr
from pydantic.json import pydantic_encoder


def custom_encoder(obj: Any) -> Any:
    """
    Custom encoder function to be passed to the default argument of json.dumps()
    :param obj: A pydantic object
    :return: An encoded pydantic object
    """
    if isinstance(obj, SecretStr):
        return obj.get_secret_value()
    return pydantic_encoder(obj)
