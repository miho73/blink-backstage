from datetime import datetime

from sqlalchemy import Column, ForeignKey
from sqlalchemy.dialects.postgresql import INTEGER, VARCHAR, TIMESTAMP
from sqlalchemy.orm import relationship, backref

from database.database import TableBase


class GoogleAuth(TableBase):
  __tablename__ = "google_auth"
  __table_args__ = {"schema": "authentication"}

  google_auth_id: int = Column(INTEGER, primary_key=True, index=True, unique=True, nullable=False, autoincrement=True)
  lookup_id: int = Column(INTEGER, ForeignKey("authentication.auth_lookup.lookup_id"), unique=True, nullable=False)
  google_id: str = Column(VARCHAR(21), nullable=False, unique=True)

  last_used: datetime = Column(TIMESTAMP)

  auth_lookup = relationship("AuthLookup", backref=backref("google_auth", uselist=False))
