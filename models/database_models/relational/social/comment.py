from datetime import datetime
from uuid import UUID as PyUUID

from sqlalchemy import Column, ForeignKey, FetchedValue
from sqlalchemy.dialects.postgresql import UUID, INTEGER, TIMESTAMP, VARCHAR, TEXT, ARRAY
from sqlalchemy.ext.mutable import MutableList
from sqlalchemy.orm import relationship, backref, Mapped

from database.database import TableBase
from models.database_models.relational.identity import Identity
from models.database_models.relational.schools import School
from models.database_models.relational.social.board import Board
from models.database_models.relational.social.post import Post


class Comment(TableBase):
  __tablename__ = "comment"
  __table_args__ = {"schema": "social"}

  comment_id: Mapped[PyUUID] = Column(UUID(as_uuid=True), primary_key=True, unique=True, index=True, nullable=False,
                                      server_default="gen_random_uuid()")

  author_id: Mapped[PyUUID] = Column(UUID(as_uuid=True), ForeignKey('users.identity.user_id'), nullable=False)
  school_id: Mapped[PyUUID] = Column(UUID(as_uuid=True), ForeignKey('school.schools.school_id'), nullable=False)
  post_id: Mapped[PyUUID] = Column(UUID(as_uuid=True), ForeignKey('social.post.post_id'), nullable=False)

  write_time: Mapped[datetime] = Column(TIMESTAMP, nullable=False, server_default="now()")

  content: Mapped[str] = Column(TEXT, nullable=False)

  upvote: Mapped[int] = Column(INTEGER, nullable=False, server_default="0")
  downvote: Mapped[int] = Column(INTEGER, nullable=False, server_default="0")

  edited: Mapped[bool] = Column(INTEGER, nullable=False, server_default=FetchedValue())

  author: Mapped[Identity] = relationship("Identity", uselist=False, backref=backref("comments",
                                                                                     uselist=True))  # TODO: decide the destiny of this post when the author is deleted
  school: Mapped[School] = relationship("School", uselist=False, backref=backref("comments",
                                                                                 uselist=True))  # TODO: decide the destiny of this post when the school is deleted
  post: Mapped[Post] = relationship(
    'Post',
    uselist=False,
    backref=backref(
      'comments',
      uselist=True,
      cascade='all, delete-orphan',
      passive_deletes=True
    )
  )
