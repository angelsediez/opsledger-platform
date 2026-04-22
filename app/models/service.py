from typing import TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base

if TYPE_CHECKING:
    from app.models.deployment import Deployment
    from app.models.incident import Incident


class Service(Base):
    __tablename__ = "services"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    owner_team: Mapped[str] = mapped_column(String(100), nullable=False)
    tier: Mapped[str] = mapped_column(String(50), nullable=False)
    description: Mapped[str] = mapped_column(String(255), nullable=False)

    deployments: Mapped[list["Deployment"]] = relationship(
        back_populates="service",
        cascade="all, delete-orphan",
    )
    incidents: Mapped[list["Incident"]] = relationship(
        back_populates="service",
        cascade="all, delete-orphan",
    )
