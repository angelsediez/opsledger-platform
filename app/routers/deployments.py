from fastapi import APIRouter

from app.schemas.deployment import Deployment, DeploymentListResponse

router = APIRouter(prefix="/deployments", tags=["deployments"])

DEPLOYMENTS = [
    Deployment(
        id=1,
        service_name="opsledger-api",
        version="0.1.0",
        environment="local",
        status="planned",
    )
]


@router.get("", response_model=DeploymentListResponse)
def list_deployments() -> DeploymentListResponse:
    return DeploymentListResponse(
        items=DEPLOYMENTS,
        total=len(DEPLOYMENTS),
        source="stub",
    )
