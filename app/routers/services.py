from fastapi import APIRouter

from app.schemas.service import Service, ServiceListResponse

router = APIRouter(prefix="/services", tags=["services"])

SERVICES = [
    Service(
        id=1,
        name="opsledger-api",
        owner_team="platform",
        tier="internal",
        description="Primary API service for OpsLedger.",
    )
]


@router.get("", response_model=ServiceListResponse)
def list_services() -> ServiceListResponse:
    return ServiceListResponse(
        items=SERVICES,
        total=len(SERVICES),
        source="stub",
    )
