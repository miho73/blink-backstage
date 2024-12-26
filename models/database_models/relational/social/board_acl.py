from enum import Enum

from sqlalchemy import Column, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, SMALLINT
from sqlalchemy.orm import Mapped

from database.database import TableBase
from uuid import UUID as PyUUID

class BoardACLType(Enum):
  ROLE = 0
  ALL = 1

class BoardACLAction(Enum):
  READ = 0
  WRITE = 1
  DELETE = 2
  MODIFY = 3
  MANAGE = 4

class BoardACL(TableBase):
  __tablename__ = "board_acl"
  __table_args__ = {"schema": "social"}

  board_id: Mapped[PyUUID] = Column(UUID(as_uuid=True), ForeignKey("social.board.board_id"), primary_key=True, index=True, nullable=False)

  _acl_type: Mapped[int] = Column("privilege_type", SMALLINT, primary_key=True, index=True, nullable=False)
  _action_code: Mapped[int] = Column("action_code", SMALLINT, primary_key=True, index=True, nullable=False)
  qualification: Mapped[int] = Column(SMALLINT, nullable=False)
  priority: Mapped[int] = Column(SMALLINT, nullable=False, server_default='999')

  @property
  def acl_type(self):
    return BoardACLType(self._acl_type)

  @acl_type.setter
  def acl_type(self, value: BoardACLType):
    self._privilege_type = value.value

  @property
  def action_code(self):
    return BoardACLAction(self._action_code)

  @action_code.setter
  def action_code(self, value: BoardACLAction):
    self._action_code = value.value
