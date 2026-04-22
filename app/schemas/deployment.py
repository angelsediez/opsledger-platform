from pydantic import BaseModel


class Deployment(BaseModel):
    id: int
    service_name: str
    version: str
    environment: str
    status: str


class DeploymentListResponse(BaseModel):
    items: list[Deployment]
    total: int
    source: str
