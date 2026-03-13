from __future__ import annotations

from datetime import datetime
from typing import List

from sqlalchemy import BigInteger, DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class User(Base):
    __tablename__ = "users"

    user_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, index=True)
    user_email: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    username: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    user_display_name: Mapped[str] = mapped_column(String, nullable=False)
    user_pwd: Mapped[str] = mapped_column(String, nullable=False)
    user_pfp_suffix: Mapped[str] = mapped_column(String, nullable=True)

    user_sessions: Mapped[List[Session]] = relationship(back_populates="session_user")


class Session(Base):
    __tablename__ = "sessions"

    session_id: Mapped[str] = mapped_column(String, primary_key=True, index=True)
    session_secret: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    expire_window: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    expire_absolute: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.user_id"), nullable=False)

    session_user: Mapped[User] = relationship(back_populates="user_sessions")
