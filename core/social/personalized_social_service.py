import logging
from uuid import UUID

from sqlalchemy.orm import Session

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
  boards = db.query(Board).all()
  ret_body = []

  for board in boards:
    exists_query = (
      db.query(StaredBoards)
      .filter_by(user_id=sub)
      .filter_by(board_id=board.board_id)
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
