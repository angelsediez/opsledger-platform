from pydantic import BaseModel, ConfigDict


class DeploymentBase(BaseModel):
    service_id: int
    version: str
    environment: str
    status: str


class DeploymentCreate(DeploymentBase):
    pass


class DeploymentRead(DeploymentBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


class DeploymentListResponse(BaseModel):
    items: list[DeploymentRead]
    total: int
    source: str
