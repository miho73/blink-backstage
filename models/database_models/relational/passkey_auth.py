from datetime import datetime

from uuid import UUID as PyUUID
from sqlalchemy import Column, ForeignKey, FetchedValue
from sqlalchemy.dialects.postgresql import INTEGER, BYTEA, TIMESTAMP, VARCHAR, CHAR, UUID
from sqlalchemy.orm import relationship, backref, Mapped

from database.database import TableBase
from models.database_models.relational.auth_lookup import AuthLookup


class PasskeyAuth(TableBase):
  __tablename__ = "passkey_auth"
  __table_args__ = {"schema": "authentication"}

  passkey_id: Mapped[PyUUID] = Column(UUID(as_uuid=True), primary_key=True, index=True, nullable=False, server_default="gen_random_uuid()")
  credential_id: Mapped[bytes] = Column(BYTEA, index=True, unique=True, nullable=False)
  lookup_id: Mapped[PyUUID] = Column(UUID(as_uuid=True), ForeignKey("authentication.auth_lookup.lookup_id"), unique=True, nullable=False)

  public_key: Mapped[bytes] = Column(BYTEA, nullable=False)
  counter: Mapped[int] = Column(INTEGER, nullable=False, server_default=FetchedValue())
  last_used: Mapped[datetime] = Column(TIMESTAMP)
  passkey_name: Mapped[str] = Column(VARCHAR(255), nullable=False)
  aaguid: Mapped[str] = Column(CHAR(36))
  created_at: Mapped[datetime] = Column(TIMESTAMP, nullable=False, server_default=FetchedValue())

  auth_lookup: Mapped[AuthLookup] = relationship("AuthLookup", backref=backref("passkey_auth", uselist=True), uselist=False)
