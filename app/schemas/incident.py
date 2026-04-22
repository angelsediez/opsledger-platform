from pydantic import BaseModel


class Incident(BaseModel):
    id: int
    service_name: str
    severity: str
    status: str
    summary: str


class IncidentListResponse(BaseModel):
    items: list[Incident]
    total: int
    source: str
