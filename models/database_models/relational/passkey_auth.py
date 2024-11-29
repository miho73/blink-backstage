from datetime import datetime

from sqlalchemy import Column, ForeignKey
from sqlalchemy.dialects.postgresql import INTEGER, BYTEA, TIMESTAMP, VARCHAR, CHAR
from sqlalchemy.orm import relationship

from database.database import TableBase


class PasskeyAuth(TableBase):
  __tablename__ = "passkey_auth"
  __table_args__ = {"schema": "authentication"}

  credential_id: bytes = Column(BYTEA, primary_key=True, index=True, unique=True, nullable=False)
  lookup_id: int = Column(INTEGER, ForeignKey("authentication.auth_lookup.lookup_id"), unique=True, nullable=False)

  public_key: bytes = Column(BYTEA, nullable=False)
  counter: int = Column(INTEGER, nullable=False, default=0)
  last_used: datetime = Column(TIMESTAMP)
  passkey_name: str = Column(VARCHAR, nullable=False)
  aaguid: str = Column(CHAR)
  created_at: datetime = Column(TIMESTAMP, nullable=False, default=datetime.now)

  auth_lookup = relationship("AuthLookup", back_populates="passkey_auth", uselist=False)
