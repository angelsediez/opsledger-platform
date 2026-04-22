from fastapi import FastAPI

from app.dependencies.runtime import get_app_metadata
from app.routers import deployments, health, incidents, services, version

metadata = get_app_metadata()

app = FastAPI(
    title="OpsLedger Platform API",
    version=metadata.app_version,
    description="Local-first operational API for services, deployments, and incidents.",
)

app.include_router(health.router)
app.include_router(version.router)
app.include_router(services.router)
app.include_router(deployments.router)
app.include_router(incidents.router)
