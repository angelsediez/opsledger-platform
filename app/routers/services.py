from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db import get_db_session
from app.models.service import Service
from app.schemas.service import ServiceCreate, ServiceListResponse, ServiceRead

router = APIRouter(prefix="/services", tags=["services"])


@router.get("", response_model=ServiceListResponse)
def list_services(db: Session = Depends(get_db_session)) -> ServiceListResponse:
    items = db.scalars(select(Service).order_by(Service.id)).all()
    return ServiceListResponse(items=items, total=len(items), source="database")


@router.post("", response_model=ServiceRead, status_code=status.HTTP_201_CREATED)
def create_service(
    payload: ServiceCreate,
    db: Session = Depends(get_db_session),
) -> ServiceRead:
    existing = db.scalar(select(Service).where(Service.name == payload.name))
    if existing is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"service '{payload.name}' already exists",
        )

    service = Service(**payload.model_dump())
    db.add(service)
    db.commit()
    db.refresh(service)
    return service
