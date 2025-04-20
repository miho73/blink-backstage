from datetime import datetime
from uuid import UUID as PyUUID

from sqlalchemy import Column, ForeignKey, UUID
from sqlalchemy.dialects.postgresql import VARCHAR, TIMESTAMP
from sqlalchemy.orm import relationship, backref, Mapped

from database.database import TableBase
from models.database_models.relational.auth_lookup import AuthLookup


class GoogleAuth(TableBase):
  __tablename__ = "google_auth"
  __table_args__ = {"schema": "authentication"}

  google_auth_id: Mapped[PyUUID] = Column(UUID(as_uuid=True), primary_key=True, index=True, unique=True, nullable=False,
                                          server_default='gen_random_uuid()')
  lookup_id: Mapped[PyUUID] = Column(UUID(as_uuid=True), ForeignKey("authentication.auth_lookup.lookup_id"),
                                     unique=True, nullable=False)
  google_id: Mapped[str] = Column(VARCHAR(21), nullable=False, unique=True)

  last_used: Mapped[datetime] = Column(TIMESTAMP)

  auth_lookup: Mapped[AuthLookup] = relationship(
    "AuthLookup",
    backref=backref(
      "google_auth",
      uselist=False,
      cascade="all, delete-orphan",
      passive_deletes=True,
    )
  )
