from functools import lru_cache
from os import getenv

from pydantic import BaseModel


class AppMetadata(BaseModel):
    app_name: str
    app_env: str
    app_version: str


@lru_cache
def get_app_metadata() -> AppMetadata:
    return AppMetadata(
        app_name=getenv("APP_NAME", "opsledger-platform"),
        app_env=getenv("APP_ENV", "local"),
        app_version=getenv("APP_VERSION", "0.1.0"),
    )
