import uuid
from datetime import datetime
from enum import Enum

from sqlalchemy import Column
from sqlalchemy.dialects.postgresql import VARCHAR, TIMESTAMP, UUID, SMALLINT, ARRAY
from sqlalchemy.ext.mutable import MutableList
from sqlalchemy.orm import Mapped

from database.database import TableBase


class BoardState(Enum):
  ACTIVE = 0
  READ_ONLY = 1
  LOCKED = 2
  CLOSED = 3


class Board(TableBase):
  __tablename__ = "board"
  __table_args__ = {"schema": "social"}

  board_id: Mapped[uuid.UUID] = Column(UUID(as_uuid=True), primary_key=True, unique=True, index=True, nullable=False,
                                    server_default="gen_random_uuid()")
  name: Mapped[str] = Column(VARCHAR(128), nullable=False)
  created_at: Mapped[datetime] = Column(TIMESTAMP, nullable=False, server_default="now()")
  tag: Mapped[list[str]] = Column(MutableList.as_mutable(ARRAY(VARCHAR(25))), nullable=False, default=[])

  _state: Mapped[int] = Column('state', SMALLINT, nullable=False, server_default="0")

  @property
  def state(self):
    return BoardState(self._state)

  @state.setter
  def state(self, value: BoardState):
    self._state = value.value
