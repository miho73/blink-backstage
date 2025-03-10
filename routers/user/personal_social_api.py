import logging
from uuid import UUID

from fastapi import APIRouter, Security, Depends, HTTPException
from sqlalchemy.orm import Session
from starlette.responses import JSONResponse

from core.authentication.authorization_service import authorization_header, authorize_jwt
from core.jwt.jwt_service import get_sub, get_aud
from core.social.personalized_social_service import get_user_personalized_board, star_board
from core.user.user_info_service import check_role
from database.database import create_connection
from models.request_models.social.personal_social_request import StarBoardRequest

log = logging.getLogger(__name__)

router = APIRouter(
  prefix='/api/user/social',
  tags=['user', 'social']
)

@router.get(
  path='/board/featured',
  tags=['board', 'recommendation'],
  description='Get user\'s featured board'
)
def get_featured_board(
  token: str = Security(authorization_header),
  db: Session = Depends(create_connection)
):
  jwt = authorize_jwt(token)
  sub = get_sub(jwt)
  aud = get_aud(jwt)

  if not check_role(aud, 'core:user'):
    raise HTTPException(status_code=403, detail='Forbidden')

  log.debug("Query user personalized board. sub=\"{}\"".format(sub))
  featured = get_user_personalized_board(sub, db)

  return JSONResponse(
    content = {
      'code': 200,
      'state': 'OK',
      'body': featured
    }
  )

@router.patch(
  '/board/star',
)
def star_board_api(
  body: StarBoardRequest,
  token: str = Security(authorization_header),
  db: Session = Depends(create_connection)
):
  jwt = authorize_jwt(token)
  sub = get_sub(jwt)
  aud = get_aud(jwt)

  if not check_role(aud, 'core:user'):
    raise HTTPException(status_code=403, detail='Forbidden')

  log.debug("Star board. sub=\"{}\", boardUUID=\"{}\" star=\"{}\"".format(sub, body.board_id, body.star))

  star_board(sub, UUID(body.board_id), body.star, db)
  db.commit()

  return JSONResponse(
    content = {
      'code': 200,
      'state': 'OK'
    }
  )
