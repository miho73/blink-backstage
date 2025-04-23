import uuid

from sqlalchemy import Column, ForeignKey, UUID
from sqlalchemy.dialects.postgresql import INTEGER
from sqlalchemy.orm import relationship, backref, Mapped

from database.database import TableBase
from models.database_models.relational.identity import Identity


class UserPreference(TableBase):
  __tablename__ = 'preference'
  __table_args__ = {'schema': "users"}

  user_id: Mapped[uuid.UUID] = Column(UUID(as_uuid=True), ForeignKey('users.identity.user_id'), unique=True,
                                      nullable=False, primary_key=True, server_default='gen_random_uuid()')

  allergy: Mapped[int] = Column(INTEGER, nullable=False, default=0)

  identity: Mapped[Identity] = relationship(
    "Identity",
    backref=backref(
      "preference",
      uselist=False,
      cascade="all, delete-orphan",
      passive_deletes=True,
    )
  )
