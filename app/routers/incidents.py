from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db import get_db_session
from app.models.incident import Incident
from app.models.service import Service
from app.schemas.incident import IncidentCreate, IncidentListResponse, IncidentRead

router = APIRouter(prefix="/incidents", tags=["incidents"])


@router.get("", response_model=IncidentListResponse)
def list_incidents(db: Session = Depends(get_db_session)) -> IncidentListResponse:
    items = db.scalars(select(Incident).order_by(Incident.id)).all()
    return IncidentListResponse(items=items, total=len(items), source="database")


@router.post("", response_model=IncidentRead, status_code=status.HTTP_201_CREATED)
def create_incident(
    payload: IncidentCreate,
    db: Session = Depends(get_db_session),
) -> IncidentRead:
    service = db.get(Service, payload.service_id)
    if service is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"service_id '{payload.service_id}' does not exist",
        )

    incident = Incident(**payload.model_dump())
    db.add(incident)
    db.commit()
    db.refresh(incident)
    return incident
