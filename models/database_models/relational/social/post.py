from datetime import datetime

from uuid import UUID as PyUUID

from sqlalchemy import Column, ForeignKey, FetchedValue
from sqlalchemy.dialects.postgresql import UUID, INTEGER, TIMESTAMP, VARCHAR, TEXT
from sqlalchemy.orm import relationship, backref

from database.database import TableBase


class Post(TableBase):
  __tablename__ = "post"
  __table_args__ = {"schema": "social"}

  post_id: PyUUID = Column(UUID(as_uuid=True), primary_key=True, unique=True, index=True, nullable=False, server_default="gen_random_uuid()")

  author_id: int = Column(INTEGER, ForeignKey('users.identity.user_id'), nullable=False)
  school_id: int = Column(INTEGER, ForeignKey('school.schools.school_id'), nullable=False)
  board_id: PyUUID = Column(UUID(as_uuid=True), ForeignKey('social.board.board_id'), nullable=False)

  write_time: datetime = Column(TIMESTAMP, nullable=False, server_default="now()")

  title: str = Column(VARCHAR(512), nullable=False)
  content: str = Column(TEXT, nullable=False)
  images: list[PyUUID] = Column(VARCHAR(512), nullable=True)

  upvote: int = Column(INTEGER, nullable=False, server_default="0")
  downvote: int = Column(INTEGER, nullable=False, server_default="0")
  views: int = Column(INTEGER, nullable=False, server_default="0")

  edited: bool = Column(INTEGER, nullable=False, server_default=FetchedValue())

  author = relationship("Identity", uselist=False, backref=backref("posts", uselist=True))
  school = relationship("School", uselist=False, backref=backref("posts", uselist=True))
  board = relationship("Board", uselist=False, backref=backref("posts", uselist=True))
