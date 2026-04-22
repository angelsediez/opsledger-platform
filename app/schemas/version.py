from pydantic import BaseModel


class VersionResponse(BaseModel):
    app_name: str
    app_version: str
    environment: str
