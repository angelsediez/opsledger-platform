from datetime import datetime

from pydantic import BaseModel


class HealthChecks(BaseModel):
    application: str
    database: str


class HealthResponse(BaseModel):
    status: str
    app_name: str
    app_version: str
    environment: str
    timestamp: datetime
    checks: HealthChecks | None = None
    note: str | None = None
