import logging
from typing import Type
from uuid import UUID as PyUUID

from sqlalchemy import asc, and_
from sqlalchemy.orm import Session

from models.database_models.relational.identity import Identity
from models.database_models.relational.social.board import Board
from models.database_models.relational.social.board_acl import BoardACL, BoardACLAction

log = logging.getLogger(__name__)


def check_acl(
  identity: Type[Identity],
  board_id: PyUUID,
  action: BoardACLAction,
  db: Session
):
  acls: list[Type[BoardACL]] = (
    db.query(BoardACL)
    .filter(
      and_(
        BoardACL.board_id == board_id,
        BoardACL._action_code == action.value
      )
    )
    .order_by(asc(BoardACL.priority))
    .all()
  )

  for acl in acls:
    if acl.qualification in identity.role:
      return True
  return False

def check_acl_by_aud(
  aud: list[str],
  board_id: PyUUID,
  action: BoardACLAction,
  db: Session
):
  acls: list[Type[BoardACL]] = (
    db.query(BoardACL)
    .filter(
      and_(
        BoardACL.board_id == board_id,
        BoardACL._action_code == action.value
      )
    )
    .order_by(asc(BoardACL.priority))
    .all()
  )

  for acl in acls:
    if acl.qualification in aud:
      return True
  return False

def create_board(
  name: str,
  db: Session
):
  new_board: Board = Board(
    name=name
  )
  db.add(new_board)
  db.flush()

  board_acls: list[BoardACL] = [
    BoardACL(
      board_id=new_board.board_id,
      qualification="root:superuser",
      action_code=BoardACLAction.WRITE,
      priority=0
    ),
    BoardACL(
      board_id=new_board.board_id,
      qualification="root:superuser",
      action_code=BoardACLAction.READ,
      priority=0
    ),
    BoardACL(
      board_id=new_board.board_id,
      qualification="root:superuser",
      action_code=BoardACLAction.MANAGE,
      priority=0
    ),
    BoardACL(
      board_id=new_board.board_id,
      qualification="root:superuser",
      action_code=BoardACLAction.UPDATE,
      priority=0
    ),
    BoardACL(
      board_id=new_board.board_id,
      qualification="root:superuser",
      action_code=BoardACLAction.DELETE,
      priority=0
    )
  ]
  db.add_all(board_acls)

  db.commit()
  return new_board.board_id
