from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db import get_db_session
from app.models.deployment import Deployment
from app.models.service import Service
from app.schemas.deployment import (
    DeploymentCreate,
    DeploymentListResponse,
    DeploymentRead,
)

router = APIRouter(prefix="/deployments", tags=["deployments"])


@router.get("", response_model=DeploymentListResponse)
def list_deployments(
    db: Session = Depends(get_db_session),
) -> DeploymentListResponse:
    items = db.scalars(select(Deployment).order_by(Deployment.id)).all()
    return DeploymentListResponse(items=items, total=len(items), source="database")


@router.post("", response_model=DeploymentRead, status_code=status.HTTP_201_CREATED)
def create_deployment(
    payload: DeploymentCreate,
    db: Session = Depends(get_db_session),
) -> DeploymentRead:
    service = db.get(Service, payload.service_id)
    if service is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"service_id '{payload.service_id}' does not exist",
        )

    deployment = Deployment(**payload.model_dump())
    db.add(deployment)
    db.commit()
    db.refresh(deployment)
    return deployment
