from datetime import datetime
from uuid import UUID
from sqlalchemy import String, TIMESTAMP, Boolean, Integer, ForeignKeyConstraint, JSON
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class CallInfo(Base):
    __tablename__ = "call_info"

    id: Mapped[UUID] = mapped_column(PG_UUID, primary_key=True)
    botId: Mapped[UUID] = mapped_column(PG_UUID, nullable=True)
    timezone: Mapped[int] = mapped_column(Integer, nullable=True)
    nps: Mapped[str | None] = mapped_column(String, nullable=True, index=True)
    duration: Mapped[int] = mapped_column(Integer, nullable=True)
    mainCallDuration: Mapped[int] = mapped_column(Integer, nullable=True)
    robotCallDuration: Mapped[int] = mapped_column(Integer, nullable=True)
    companyId: Mapped[int] = mapped_column(Integer, nullable=True)
    isIncoming: Mapped[bool] = mapped_column(Boolean, nullable=True)
    createdAt: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), nullable=False, index=True
    )
    startedAt: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), nullable=True, index=True
    )
    finishedAt: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), nullable=True, index=True
    )
    status: Mapped[str] = mapped_column(String(225), nullable=True)
    currentStatusName: Mapped[str] = mapped_column(String(225), nullable=True)
    confirmation: Mapped[str] = mapped_column(String(225), nullable=True)
    evaluation: Mapped[str] = mapped_column(String(225), nullable=True)
    autoCallCandidateId: Mapped[str] = mapped_column(String(225), nullable=True)
    dialogResult: Mapped[str] = mapped_column(String(500), nullable=True)
    resultsString: Mapped[JSON] = mapped_column(JSON, nullable=True)
    redash_variable: Mapped[JSON] = mapped_column(JSON, nullable=True)
    redash_result: Mapped[JSON] = mapped_column(JSON, nullable=True)
    project: Mapped[str] = mapped_column(String(225), nullable=False)
    markersString: Mapped[str] = mapped_column(String(225), nullable=True)

    __table_args__ = (ForeignKeyConstraint(["project"], ["twin_projects.twin_login"]),)


class TwinProjects(Base):
    __tablename__ = "twin_projects"

    id: Mapped[str] = mapped_column(Integer, autoincrement=True, primary_key=True)
    twin_login: Mapped[str] = mapped_column(String(225), unique=True)
    twin_password: Mapped[str] = mapped_column(String(225))
    is_active: Mapped[bool] = mapped_column(Boolean)
