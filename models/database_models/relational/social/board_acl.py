from enum import Enum
from uuid import UUID as PyUUID

from sqlalchemy import Column, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, SMALLINT
from sqlalchemy.orm import Mapped, relationship, backref

from database.database import TableBase
from models.database_models.relational.social.board import Board


class BoardACLAction(Enum):
  READ = 0
  WRITE = 1
  DELETE = 2
  UPDATE = 3
  MANAGE = 4


class BoardACL(TableBase):
  __tablename__ = "board_acl"
  __table_args__ = {"schema": "social"}

  board_id: Mapped[PyUUID] = Column(UUID(as_uuid=True), ForeignKey("social.board.board_id"), primary_key=True,
                                    index=True, nullable=False)

  _action_code: Mapped[int] = Column("action_code", SMALLINT, primary_key=True, index=True, nullable=False)
  qualification: Mapped[int] = Column(SMALLINT, nullable=False, primary_key=True)
  priority: Mapped[int] = Column(SMALLINT, nullable=False, server_default='999')

  board: Mapped[Board] = relationship(
    'Board',
    uselist=False,
    backref=backref(
      'acls',
      uselist=True,
      cascade='all, delete-orphan',
      passive_deletes=True
    )
  )

  @property
  def action_code(self):
    return BoardACLAction(self._action_code)

  @action_code.setter
  def action_code(self, value: BoardACLAction):
    self._action_code = value.value
