from fastapi import APIRouter

from app.schemas.incident import Incident, IncidentListResponse

router = APIRouter(prefix="/incidents", tags=["incidents"])

INCIDENTS = [
    Incident(
        id=1,
        service_name="opsledger-api",
        severity="low",
        status="open",
        summary="Sample incident used to validate API structure before database integration.",
    )
]


@router.get("", response_model=IncidentListResponse)
def list_incidents() -> IncidentListResponse:
    return IncidentListResponse(
        items=INCIDENTS,
        total=len(INCIDENTS),
        source="stub",
    )
