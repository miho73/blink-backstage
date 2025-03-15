import logging
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy import cast
from sqlalchemy.dialects.postgresql import TEXT
from sqlalchemy.orm import Session
from sqlalchemy.sql.operators import or_

from core.user.user_info_service import get_identity_by_userid, role_to_school
from models.database_models.relational.social.board import Board
from models.database_models.relational.social.stared_boards import StaredBoards

log = logging.getLogger(__name__)

def star_board(
  sub: UUID,
  board_uuid: UUID,
  star: bool,
  db: Session
):
  current_state = (
    db.query(StaredBoards)
      .filter(StaredBoards.user_id == sub, StaredBoards.board_id == board_uuid)
      .first()
  )

  if current_state is None:
    if star:
      log.debug("Starred board: sub=\"{}\", board=\"{}\"".format(sub, board_uuid))
      db.add(StaredBoards(user_id=sub, board_id=board_uuid))
    else:
      log.debug("User has not starred the board: sub=\"{}\", board=\"{}\"".format(sub, board_uuid))
  else:
    if star:
      log.debug("User has already starred the board: sub=\"{}\", board=\"{}\"".format(sub, board_uuid))
    else:
      log.debug("Removed star from the board: sub=\"{}\", board=\"{}\"".format(sub, board_uuid))
      db.delete(current_state)


def get_user_personalized_board(
  sub: UUID,
  db: Session
):
  ret_body = []

  identity = get_identity_by_userid(sub, db)
  student_verified, neis_code = role_to_school(identity.role)

  if not student_verified:
    raise HTTPException(status_code=403, detail='Forbidden')

  boards = (
    db.query(Board)
    .filter(
      or_(
        Board.board_id.in_(
          db.query(StaredBoards.board_id)
          .filter(StaredBoards.user_id == sub)
        ),
        cast(Board.tag, TEXT).contains(neis_code)
      )
    )
    .all()
  )

  for board in boards:
    exists_query = (
      db.query(StaredBoards)
      .filter_by(user_id=sub, board_id=board.board_id)
      .exists()
    )
    exists = db.query(exists_query).scalar()

    ret_body.append({
      'boardName': board.name,
      'boardUUID': str(board.board_id),
      'stared': exists
    })

  log.debug("User personalized boards are: sub=\"{}\", count:\"{}\"".format(sub, len(ret_body)))

  return ret_body
