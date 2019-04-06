from typing import Tuple

from pydantic import BaseModel, SecretStr


class ArtifactoryModel(BaseModel):
    url: str
    api_key: SecretStr = None
    auth: Tuple[str, SecretStr] = None
