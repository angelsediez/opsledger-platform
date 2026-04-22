from datetime import UTC, datetime

from fastapi import APIRouter, Depends

from app.dependencies.runtime import AppMetadata, get_app_metadata
from app.schemas.health import HealthChecks, HealthResponse

router = APIRouter(prefix="/health", tags=["health"])


@router.get("/live", response_model=HealthResponse)
def get_liveness(
    metadata: AppMetadata = Depends(get_app_metadata),
) -> HealthResponse:
    return HealthResponse(
        status="ok",
        app_name=metadata.app_name,
        app_version=metadata.app_version,
        environment=metadata.app_env,
        timestamp=datetime.now(UTC),
        checks=HealthChecks(application="ok", database="not-configured-yet"),
        note="Liveness only checks that the API process is responding.",
    )


@router.get("/ready", response_model=HealthResponse)
def get_readiness(
    metadata: AppMetadata = Depends(get_app_metadata),
) -> HealthResponse:
    return HealthResponse(
        status="ok",
        app_name=metadata.app_name,
        app_version=metadata.app_version,
        environment=metadata.app_env,
        timestamp=datetime.now(UTC),
        checks=HealthChecks(application="ok", database="deferred-to-phase-03"),
        note="Readiness is provisional in Phase 02; PostgreSQL validation starts in Phase 03.",
    )
