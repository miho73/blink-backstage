import datetime

from sqlalchemy import Column, ForeignKey
from sqlalchemy.dialects.postgresql import INTEGER, VARCHAR, CHAR, TIMESTAMP
from sqlalchemy.orm import relationship, backref

from database.database import TableBase


class PasswordAuth(TableBase):
  __tablename__ = "password_auth"
  __table_args__ = {"schema": "authentication"}

  password_auth_id: int = Column(INTEGER, primary_key=True, index=True, unique=True, nullable=False, autoincrement=True)
  lookup_id: int = Column(INTEGER, ForeignKey("authentication.auth_lookup.lookup_id"), unique=True, nullable=False)
  auth_lookup = relationship("AuthLookup", backref=backref("password_auth", uselist=False))

  user_id: str = Column(VARCHAR(255), nullable=False, unique=True, index=True)
  password: str = Column(CHAR(60), nullable=False)

  last_changed: datetime = Column(TIMESTAMP, nullable=False, server_default="now()")
  last_used: datetime = Column(TIMESTAMP)
