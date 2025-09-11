"""
Definition of all utils.
"""
from __future__ import annotations

from typing import Any

from pydantic import SecretStr
from pydantic_core import to_jsonable_python


def custom_encoder(obj: Any) -> Any:
    """
    Custom encoder function to be passed to the default argument of json.dumps()
    :param obj: A pydantic object
    :return: An encoded pydantic object
    """
    if isinstance(obj, SecretStr):
        return obj.get_secret_value()
    return to_jsonable_python(obj)


def remove_suffix(text: str, suffix: str) -> str:
    """
    Remove a suffix from a string if it exists.
    :param text: The original string
    :param suffix: The suffix to remove
    :return: The string without the suffix if it existed, otherwise the original string
    """
    if text.endswith(suffix):
        return text[: -len(suffix)]
    return text
