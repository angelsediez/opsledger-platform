from fastapi import APIRouter, Depends

from app.dependencies.runtime import AppMetadata, get_app_metadata
from app.schemas.version import VersionResponse

router = APIRouter(tags=["version"])


@router.get("/version", response_model=VersionResponse)
def get_version(
    metadata: AppMetadata = Depends(get_app_metadata),
) -> VersionResponse:
    return VersionResponse(
        app_name=metadata.app_name,
        app_version=metadata.app_version,
        environment=metadata.app_env,
    )
