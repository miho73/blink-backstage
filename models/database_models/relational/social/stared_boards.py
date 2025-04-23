import uuid

from sqlalchemy import Column, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, relationship, backref

from database.database import TableBase
from models.database_models.relational.identity import Identity
from models.database_models.relational.social.board import Board


class StaredBoards(TableBase):
  __tablename__ = 'stared_boards'
  __table_args__ = {'schema': 'social'}

  user_id: Mapped[uuid.UUID] = Column(UUID(as_uuid=True), ForeignKey('users.identity.user_id'), primary_key=True,
                                      nullable=False)
  board_id: Mapped[uuid.UUID] = Column(UUID(as_uuid=True), ForeignKey('social.board.board_id'), primary_key=True,
                                       nullable=False)

  referred_board: Mapped[Board] = relationship(
    'Board',
    uselist=False,
    backref=backref(
      'star_list',
      uselist=True,
      cascade='all, delete-orphan',
      passive_deletes=True,
    )
  )
  who_starred: Mapped[Identity] = relationship(
    'Identity',
    uselist=False,
    backref=backref(
      'star_list',
      uselist=True,
      cascade='all, delete-orphan',
      passive_deletes=True,
    )
  )
