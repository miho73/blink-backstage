import logging
from typing import Type
from uuid import UUID as PyUUID

from sqlalchemy import asc, and_
from sqlalchemy.orm import Session

from models.database_models.relational.identity import Identity
from models.database_models.relational.social.board_acl import BoardACL, BoardACLType, BoardACLAction

log = logging.getLogger(__name__)


def check_privilege(
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
        BoardACL.action_code == action
      )
    )
    .order_by(asc(BoardACL.priority))
    .all()
  )

  for acl in acls:
    if acl.acl_type is BoardACLType.ALL:
      return True
    if acl.acl_type is BoardACLType.SCHOOL_ID:
      if identity.school_id == acl.qualification:
        return True

  return False
