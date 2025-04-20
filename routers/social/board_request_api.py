import logging
import re
from uuid import UUID

from fastapi import Depends, HTTPException, APIRouter
from fastapi.params import Security
from sqlalchemy.orm import Session
from starlette.responses import JSONResponse

from core.authentication.authorization_service import authorization_header, authorize_jwt
from core.jwt.jwt_service import get_aud
from core.social import board_service, check_acl
from core.social.board_service import check_acl_by_aud
from core.user.user_info_service import check_role
from core.validation import validate_all, length_check
from database.database import create_connection
from models.database_models.relational.social.board_acl import BoardACL, BoardACLAction
from models.request_models.social.board_request import CreateBoardRequest

log = logging.getLogger(__name__)

router = APIRouter(
  prefix="/api/social/board",
  tags=["board"]
)


@router.post(
  path="",
  description="Create a new board",
)
async def create_board(
  body: CreateBoardRequest,
  jwt: str = Security(authorization_header),
  db: Session = Depends(create_connection)
):
  log.debug(f"Creating board. board_name=\"{body.name}\"")

  token = authorize_jwt(jwt)
  aud = token.get("aud")

  if check_role(aud, "social:add_board"):
    board_id = board_service.create_board(body.name, db)
    log.debug(f"Board created. board_id=\"{board_id}\"")
    return JSONResponse(
      status_code=201,
      content={
        'code': 201,
        'state': 'CREATED',
        'boardId': str(board_id)
      }
    )
  else:
    raise HTTPException(403, "User does not have permission to add boards")

@router.get(
  path="/{board_id}",
  description="Get board information",
)
async def get_board(
  board_id: str,
  jwt: str = Security(authorization_header),
  db: Session = Depends(create_connection)
):
  log.debug(f"Getting board. board_id=\"{board_id}\"")

  token = authorize_jwt(jwt)
  aud = get_aud(token)

  if board_id is None:
    raise HTTPException(400, "board_id is required")
  if not re.match('^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$', board_id):
    raise HTTPException(400, "board_id is not a valid UUID")

  bid = UUID(board_id)

  if check_acl_by_aud(aud, bid, BoardACLAction.READ, db):
    board = board_service.get_board(bid, db)
    log.debug(f"Board found. board_id=\"{board_id}\"")

    return JSONResponse(
      status_code=200,
      content={
        'code': 200,
        'state': 'OK',
        'board': board
      }
    )
  else:
    raise HTTPException(403, "User does not have permission to read this board")

@router.get(
  path="",
  description="Get board by its name",
)
def get_board_by_name(
  name: str,
  jwt: str = Security(authorization_header),
  db: Session = Depends(create_connection)
):
  log.debug(f"Getting board. board_name=\"{name}\"")

  token = authorize_jwt(jwt)
  aud = token.get("aud")

  if name is None:
    raise HTTPException(400, "name is required")
  if validate_all(
    length_check(name, 1, 512)
  ):
    raise HTTPException(400, "name is too long or too short")

  board = board_service.get_board_by_name(name, aud, db)

  return JSONResponse(
    status_code=200,
    content={
      'code': 200,
      'state': 'OK',
      'board': board
    }
  )
