# Copyright (c) 2019 Ananias
# Copyright (c) 2023 Helio Chissini de Castro
#
# Licensed under the MIT license: https://opensource.org/licenses/MIT
# Permission is granted to use, copy, modify, and redistribute the work.
# Full license information available in the project LICENSE file.
#
# SPDX-License-Identifier: MIT

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
