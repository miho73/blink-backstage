from datetime import datetime

from sqlalchemy import Column, ForeignKey
from sqlalchemy.dialects.postgresql import INTEGER, UUID, TIMESTAMP
from sqlalchemy.orm import relationship, backref, Mapped

from database.database import TableBase

from uuid import UUID as PyUUID

from models.database_models.relational.identity import Identity


class PostImage(TableBase):
  __tablename__ = "image"
  __table_args__ = {"schema": "social"}

  image_id: Mapped[PyUUID] = Column(UUID(as_uuid=True), primary_key=True, index=True, unique=True, nullable=False, server_default="gen_random_uuid()")

  upload_by: Mapped[PyUUID] = Column(UUID(as_uuid=True), ForeignKey("users.identity.user_id"), nullable=False)
  upload_at: Mapped[datetime] = Column(TIMESTAMP, nullable=False, server_default="now()")
  image: Mapped[bytes] = Column("image", nullable=False)

  uploader: Mapped[Identity] = relationship("Identity", uselist=False, backref=backref("uploaded", uselist=True))
