from datetime import datetime

from uuid import UUID as PyUUID
from sqlalchemy import Column, ForeignKey, FetchedValue
from sqlalchemy.dialects.postgresql import INTEGER, BYTEA, TIMESTAMP, VARCHAR, CHAR, UUID
from sqlalchemy.orm import relationship, backref

from database.database import TableBase


class PasskeyAuth(TableBase):
  __tablename__ = "passkey_auth"
  __table_args__ = {"schema": "authentication"}

  passkey_id: PyUUID = Column(UUID(as_uuid=True), primary_key=True, index=True, nullable=False, server_default="gen_random_uuid()")
  credential_id: bytes = Column(BYTEA, index=True, unique=True, nullable=False)
  lookup_id: int = Column(INTEGER, ForeignKey("authentication.auth_lookup.lookup_id"), unique=True, nullable=False)

  public_key: bytes = Column(BYTEA, nullable=False)
  counter: int = Column(INTEGER, nullable=False, server_default=FetchedValue())
  last_used: datetime = Column(TIMESTAMP)
  passkey_name: str = Column(VARCHAR(255), nullable=False)
  aaguid: str = Column(CHAR(36))
  created_at: datetime = Column(TIMESTAMP, nullable=False, server_default=FetchedValue())

  auth_lookup = relationship("AuthLookup", backref=backref("passkey_auth", uselist=True), uselist=False)
