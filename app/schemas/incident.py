from pydantic import BaseModel, ConfigDict


class IncidentBase(BaseModel):
    service_id: int
    severity: str
    status: str
    summary: str


class IncidentCreate(IncidentBase):
    pass


class IncidentRead(IncidentBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


class IncidentListResponse(BaseModel):
    items: list[IncidentRead]
    total: int
    source: str
