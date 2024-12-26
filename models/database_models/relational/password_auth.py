import datetime

from sqlalchemy import Column, ForeignKey, UUID
from sqlalchemy.dialects.postgresql import INTEGER, VARCHAR, CHAR, TIMESTAMP
from sqlalchemy.orm import relationship, backref, Mapped

from database.database import TableBase
from uuid import UUID as PyUUID

from models.database_models.relational.auth_lookup import AuthLookup


class PasswordAuth(TableBase):
  __tablename__ = "password_auth"
  __table_args__ = {"schema": "authentication"}

  password_auth_id: Mapped[PyUUID] = Column(UUID(as_uuid=True), primary_key=True, index=True, unique=True, nullable=False, server_default='gen_random_uuid()')
  lookup_id: Mapped[PyUUID] = Column(INTEGER, ForeignKey("authentication.auth_lookup.lookup_id"), unique=True, nullable=False)
  auth_lookup: Mapped[AuthLookup] = relationship("AuthLookup", backref=backref("password_auth", uselist=False))

  user_id: Mapped[str] = Column(VARCHAR(255), nullable=False, unique=True, index=True)
  password: Mapped[str] = Column(CHAR(60), nullable=False)

  last_changed: Mapped[datetime] = Column(TIMESTAMP, nullable=False, server_default="now()")
  last_used: Mapped[datetime] = Column(TIMESTAMP)
