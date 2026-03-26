from __future__ import annotations

import enum
from datetime import date, datetime, time
from typing import List

from sqlalchemy import (
    BigInteger,
    CheckConstraint,
    Date,
    DateTime,
    ForeignKey,
    String,
    Text,
    Time,
)
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


# ENUMS --------------------------------------------------------------------------------------------
class OrganizerMemberStatus(str, enum.Enum):
    INVITED = "INVITED"
    JOINED = "JOINED"


class EventPublicationStatus(str, enum.Enum):
    DRAFT = "DRAFT"
    PUBLIC = "PUBLIC"


# Users --------------------------------------------------------------------------------------------
class User(Base):
    __tablename__ = "users"

    user_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, index=True)
    user_email: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    username: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    user_display_name: Mapped[str] = mapped_column(String, nullable=False)
    user_pwd: Mapped[str] = mapped_column(String, nullable=False)
    user_pfp_suffix: Mapped[str] = mapped_column(String, nullable=True)

    user_sessions: Mapped[List[Session]] = relationship(back_populates="session_user")
    user_orgs_as_head: Mapped[List[OrganizerGroup]] = relationship(back_populates="head_user")
    user_org_memberships: Mapped[List[OrganizerMember]] = relationship(back_populates="user")


# Authentication -----------------------------------------------------------------------------------
class Session(Base):
    __tablename__ = "sessions"

    session_id: Mapped[str] = mapped_column(String, primary_key=True, index=True)
    session_secret: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    expire_window: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    expire_absolute: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.user_id"), nullable=False)

    session_user: Mapped[User] = relationship(back_populates="user_sessions")


# Event Management ---------------------------------------------------------------------------------
class OrganizerGroup(Base):
    __tablename__ = "orgs"

    org_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, index=True)
    org_unique_name: Mapped[str] = mapped_column(String, unique=True, nullable=False, index=True)
    org_display_name: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    org_head_user_id: Mapped[int] = mapped_column(ForeignKey("users.user_id"), nullable=False)

    head_user: Mapped[User] = relationship(back_populates="user_orgs_as_head")
    org_members: Mapped[List[OrganizerMember]] = relationship(back_populates="org")
    org_events: Mapped[List[Event]] = relationship(back_populates="event_organizer")


class OrganizerMember(Base):
    __tablename__ = "org_members"

    user_id: Mapped[int] = mapped_column(ForeignKey("users.user_id"), primary_key=True, index=True)
    org_id: Mapped[int] = mapped_column(ForeignKey("orgs.org_id"), primary_key=True, index=True)
    status: Mapped[OrganizerMemberStatus] = mapped_column(
        SQLEnum(OrganizerMemberStatus),
        default=OrganizerMemberStatus.INVITED,
        nullable=False,
    )

    user: Mapped[User] = relationship(back_populates="user_org_memberships")
    org: Mapped[OrganizerGroup] = relationship(back_populates="org_members")


class Event(Base):
    __tablename__ = "events"

    event_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, index=True)
    event_org_id: Mapped[int] = mapped_column(ForeignKey("orgs.org_id"), nullable=False)
    event_name: Mapped[str] = mapped_column(String, nullable=False)
    event_safe_name: Mapped[str] = mapped_column(String, nullable=False)  # For slugs
    event_suffix: Mapped[str] = mapped_column(String, nullable=False)  # For slugs
    event_description: Mapped[str] = mapped_column(Text)
    event_location: Mapped[str] = mapped_column(String)
    event_application_info: Mapped[str] = mapped_column(Text)
    event_application_accept_start: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    event_application_accept_end: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    event_map_img_suffix: Mapped[str] = mapped_column(String, nullable=True)
    event_map_data_suffix: Mapped[str] = mapped_column(String, nullable=True)
    event_publication_status: Mapped[EventPublicationStatus] = mapped_column(
        SQLEnum(EventPublicationStatus),
        default=EventPublicationStatus.DRAFT,
        nullable=False,
    )

    event_organizer: Mapped[OrganizerGroup] = relationship(back_populates="org_events")
    event_days: Mapped[List[EventDay]] = relationship(back_populates="event")

    __table_args__ = (
        CheckConstraint(
            "event_application_accept_start < event_application_accept_end",
            name="check_valid_application_date",
        ),
        CheckConstraint(
            "event_publication_status = 'DRAFT' OR "
            "(event_description IS NOT NULL AND "
            "event_location IS NOT NULL AND "
            "event_application_info IS NOT NULL AND "
            "event_application_accept_start IS NOT NULL AND "
            "event_application_accept_end IS NOT NULL AND "
            "event_map_img_suffix IS NOT NULL)"
            "event_map_data_suffix IS NOT NULL)",
            name="check_public_event_completeness",
        ),
    )


# --------------------------------------------------------------------------------------------------
# TODO: Add EventMembers for permission settings.
# --------------------------------------------------------------------------------------------------


class EventDay(Base):
    __tablename__ = "event_days"

    eventday_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, index=True)
    belong_in_event_id: Mapped[int] = mapped_column(ForeignKey("events.event_id"), nullable=False)
    eventday_date: Mapped[date] = mapped_column(Date, nullable=False)
    eventday_time_start: Mapped[time] = mapped_column(Time, nullable=False)
    eventday_time_end: Mapped[time] = mapped_column(Time, nullable=False)
    eventday_timezone: Mapped[str] = mapped_column(String, nullable=False)  # IANA timezone string

    __table_args__ = (
        CheckConstraint(
            "eventday_time_start < eventday_time_end",
            name="check_eventday_times_valid",
        ),
    )

    event: Mapped[Event] = relationship(back_populates="event_days")
