from datetime import datetime

from sqlalchemy import Column, ForeignKey
from sqlalchemy.dialects.postgresql import INTEGER, CHAR, TIMESTAMP
from sqlalchemy.orm import relationship, backref

from database.database import TableBase

from uuid import UUID as PyUUID

class PostImage(TableBase):
  __tablename__ = "image"
  __table_args__ = {"schema": "social"}

  image_id: str = Column(CHAR(64), primary_key=True, index=True, unique=True, nullable=False)

  upload_by: int = Column(INTEGER, ForeignKey("users.identity.user_id"), nullable=False)
  upload_at: datetime = Column(TIMESTAMP, nullable=False, server_default="now()")
  image: bytes = Column("image", nullable=False)

  uploader = relationship("Identity", uselist=False, backref=backref("uploaded", uselist=True))
