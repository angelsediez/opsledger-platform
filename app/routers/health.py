from datetime import UTC, datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.db import get_db_session
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
        checks=HealthChecks(application="ok", database="not-checked"),
        note="Liveness only checks that the API process is responding.",
    )


@router.get("/ready", response_model=HealthResponse)
def get_readiness(
    metadata: AppMetadata = Depends(get_app_metadata),
    db: Session = Depends(get_db_session),
) -> HealthResponse:
    try:
        db.execute(text("SELECT 1"))
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "status": "error",
                "database": "unreachable",
                "message": str(exc),
            },
        ) from exc

    return HealthResponse(
        status="ok",
        app_name=metadata.app_name,
        app_version=metadata.app_version,
        environment=metadata.app_env,
        timestamp=datetime.now(UTC),
        checks=HealthChecks(application="ok", database="ok"),
        note="Readiness validates both API responsiveness and database reachability.",
    )
