from pydantic import BaseModel


class Service(BaseModel):
    id: int
    name: str
    owner_team: str
    tier: str
    description: str


class ServiceListResponse(BaseModel):
    items: list[Service]
    total: int
    source: str
