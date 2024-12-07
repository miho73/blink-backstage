from enum import Enum

from sqlalchemy import Column, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, INTEGER
from database.database import TableBase
from uuid import UUID as PyUUID

class BoardPrivilegeType(Enum):
  SCHOOL_ID = 0
  ROLE = 1

class BoardPrivilegeAction(Enum):
  READ = 0
  WRITE = 1
  DELETE = 2
  MODIFY = 3

class BoardPrivilege(TableBase):
  __tablename__ = "board_privilege"
  __table_args__ = {"schema": "social"}

  board_id: PyUUID = Column(UUID(as_uuid=True), ForeignKey("social.board.board_id"), primary_key=True, index=True, nullable=False)

  _privilege_type: int = Column("privilege_type", INTEGER, primary_key=True, index=True, nullable=False)
  _action_code: int = Column("action_code", INTEGER, primary_key=True, index=True, nullable=False)
  qualification: int = Column(INTEGER, nullable=False)
