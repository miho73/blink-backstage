from datetime import datetime
from typing import Optional

from pydantic import EmailStr
from sqlalchemy import Column, ForeignKey, UUID
from sqlalchemy.dialects.postgresql import INTEGER, VARCHAR, BOOLEAN, SMALLINT, TIMESTAMP, ARRAY
from sqlalchemy.ext.mutable import MutableList
from sqlalchemy.orm import relationship, backref, Mapped

from database.database import TableBase
from uuid import UUID as PyUUID


class Identity(TableBase):
  __tablename__ = "identity"
  __table_args__ = {"schema": "users"}

  user_id: Mapped[PyUUID] = Column(UUID(as_uuid=True), primary_key=True, index=True, unique=True, nullable=False, server_default="gen_random_uuid()")
  username: Mapped[str] = Column(VARCHAR(100), nullable=False)

  email: Mapped[EmailStr] = Column(VARCHAR(255), nullable=False, unique=True)
  email_verified: Mapped[bool] = Column(BOOLEAN, nullable=False, default=False)

  join_date: Mapped[datetime] = Column(TIMESTAMP, nullable=False, default="now()")
  last_login: Mapped[datetime] = Column(TIMESTAMP)

  grade: Mapped[Optional[int]] = Column(SMALLINT)
  role: Mapped[list[str]] = Column(MutableList.as_mutable(ARRAY(VARCHAR(45))), nullable=False, default=['core:user'])

