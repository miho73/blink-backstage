import uuid

from sqlalchemy import Column, ForeignKey
from sqlalchemy.orm import Mapped, relationship, backref
from sqlalchemy.dialects.postgresql import UUID, BOOLEAN

from database.database import TableBase
from models.database_models.relational.identity import Identity
from models.database_models.relational.social.post import Post


class Votes(TableBase):
  __tablename__ = 'votes'
  __table_args__ = {'schema': 'social'}

  user_id: Mapped[uuid.UUID] = Column(UUID(as_uuid=True), ForeignKey('users.identity.user_id'), primary_key=True, nullable=False)
  post_id: Mapped[uuid.UUID] = Column(UUID(as_uuid=True), ForeignKey('social.post.post_id'), primary_key=True, nullable=False)

  vote: Mapped[bool] = Column(BOOLEAN, nullable=False)

  post: Mapped[Post] = relationship(
    'Post',
    uselist=False,
    backref=backref(
      'votes',
      uselist=True,
      cascade='all, delete-orphan',
      passive_deletes=True
    )
  )
  voter: Mapped[Identity] = relationship(
    'Identity',
    uselist=False,
    backref=backref(
      'votes',
      uselist=True,
      cascade='all, delete-orphan',
      passive_deletes=True
    )
  )
