from uuid import UUID as PyUUID

from sqlalchemy import Column, ForeignKey, FetchedValue, UUID
from sqlalchemy.dialects.postgresql import BOOLEAN, SMALLINT
from sqlalchemy.orm import relationship, backref, Mapped

from database.database import TableBase
from models.database_models.relational.identity import Identity


class AuthLookup(TableBase):
  __tablename__ = "auth_lookup"
  __table_args__ = {"schema": "authentication"}

  lookup_id: Mapped[PyUUID] = Column(UUID(as_uuid=True), primary_key=True, index=True, unique=True, nullable=False,
                                     server_default='gen_random_uuid()')
  user_id: Mapped[PyUUID] = Column(UUID(as_uuid=True), ForeignKey("users.identity.user_id"), unique=True,
                                   nullable=False, index=True)

  google: Mapped[bool] = Column(BOOLEAN, nullable=False, server_default=FetchedValue())
  password: Mapped[bool] = Column(BOOLEAN, nullable=False, server_default=FetchedValue())
  passkey: Mapped[int] = Column(SMALLINT, nullable=False, server_default=FetchedValue())

  identity: Mapped[Identity] = relationship("Identity", uselist=False, backref=backref("auth_lookup", uselist=False))
