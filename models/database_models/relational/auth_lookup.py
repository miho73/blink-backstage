from sqlalchemy import Column, ForeignKey, FetchedValue
from sqlalchemy.dialects.postgresql import INTEGER, BOOLEAN, SMALLINT
from sqlalchemy.orm import relationship, backref

from database.database import TableBase


class AuthLookup(TableBase):
  __tablename__ = "auth_lookup"
  __table_args__ = {"schema": "authentication"}

  lookup_id: int = Column(INTEGER, primary_key=True, index=True, unique=True, nullable=False, autoincrement=True)
  user_id: int = Column(INTEGER, ForeignKey("users.identity.user_id"), unique=True, nullable=False, index=True)

  google = Column(BOOLEAN, nullable=False, server_default=FetchedValue())
  password = Column(BOOLEAN, nullable=False, server_default=FetchedValue())
  passkey = Column(SMALLINT, nullable=False, server_default=FetchedValue())

  identity = relationship("Identity", backref=backref("auth_lookup", uselist=False))
