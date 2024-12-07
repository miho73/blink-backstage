from datetime import datetime
from enum import Enum

from uuid import UUID as PyUUID
from sqlalchemy import Column, ForeignKey
from sqlalchemy.dialects.postgresql import INTEGER, VARCHAR, TIMESTAMP, UUID, SMALLINT
from sqlalchemy.orm import relationship

from database.database import TableBase

class BoardState(Enum):
  ACTIVE = 0
  READ_ONLY = 1
  LOCKED = 2
  CLOSED = 3

class Board(TableBase):
  __tablename__ = "board"
  __table_args__ = {"schema": "social"}

  board_id: PyUUID = Column(UUID(as_uuid=True), primary_key=True, unique=True, index=True, nullable=False, server_default="gen_random_uuid()")
  name: str = Column(VARCHAR(128), nullable=False)
  owner_id: int = Column(INTEGER, ForeignKey("users.identity.user_id"), nullable=False)
  created_at: datetime = Column(TIMESTAMP, nullable=False, server_default="now()")

  _state: int = Column('state', SMALLINT, nullable=False, server_default="0")

  owner = relationship("User", back_populates="boards")

  @property
  def state(self):
    return BoardState(self._state)

  @state.setter
  def state(self, value: BoardState):
    self._state = value.value
