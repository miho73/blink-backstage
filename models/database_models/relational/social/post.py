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


class Post(TableBase):
  __tablename__ = "post"
  __table_args__ = {"schema": "social"}

  post_id: Mapped[PyUUID] = Column(UUID(as_uuid=True), primary_key=True, unique=True, index=True, nullable=False, server_default="gen_random_uuid()")

  author_id: Mapped[PyUUID] = Column(UUID(as_uuid=True), ForeignKey('users.identity.user_id'), nullable=False)
  school_id: Mapped[PyUUID] = Column(UUID(as_uuid=True), ForeignKey('school.schools.school_id'), nullable=False)
  board_id: Mapped[PyUUID] = Column(UUID(as_uuid=True), ForeignKey('social.board.board_id'), nullable=False)

  write_time: Mapped[datetime] = Column(TIMESTAMP, nullable=False, server_default="now()")

  title: Mapped[str] = Column(VARCHAR(512), nullable=False)
  content: Mapped[str] = Column(TEXT, nullable=False)
  images: Mapped[list[PyUUID]] = Column(MutableList.as_mutable(ARRAY(UUID(as_uuid=True))), nullable=True)

  upvote: Mapped[int] = Column(INTEGER, nullable=False, server_default="0")
  downvote: Mapped[int] = Column(INTEGER, nullable=False, server_default="0")
  views: Mapped[int] = Column(INTEGER, nullable=False, server_default="0")

  edited: Mapped[bool] = Column(INTEGER, nullable=False, server_default=FetchedValue())

  author: Mapped[Identity] = relationship("Identity", uselist=False, backref=backref("posts", uselist=True))
  school: Mapped[School] = relationship("School", uselist=False, backref=backref("posts", uselist=True))
  board: Mapped[Board] = relationship("Board", uselist=False, backref=backref("posts", uselist=True))
