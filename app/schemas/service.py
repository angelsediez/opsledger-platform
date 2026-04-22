from pydantic import BaseModel, ConfigDict


class ServiceBase(BaseModel):
    name: str
    owner_team: str
    tier: str
    description: str


class ServiceCreate(ServiceBase):
    pass


class ServiceRead(ServiceBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


class ServiceListResponse(BaseModel):
    items: list[ServiceRead]
    total: int
    source: str
