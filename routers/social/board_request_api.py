import logging

from fastapi import Depends, HTTPException, APIRouter
from fastapi.params import Security
from sqlalchemy.orm import Session
from starlette.responses import JSONResponse

from core.authentication.authorization_service import authorization_header, authorize_jwt
from core.social import board_service
from core.user.user_info_service import check_role
from database.database import create_connection
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
