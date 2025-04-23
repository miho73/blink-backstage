import logging

from fastapi import APIRouter, Security, Depends, Request, HTTPException
from sqlalchemy.orm import Session
from starlette.responses import JSONResponse

from core.authentication.authorization_service import authorization_header, authorize_jwt
from core.jwt.jwt_service import get_sub, get_aud
from core.user.user_access_service import access_get_user
from core.user.user_info_service import check_role
from database.database import create_connection

log = logging.getLogger(__name__)

router = APIRouter(
  prefix='/api/user/access',
  tags=['user', 'access api']
)


@router.get(
  path='',
  summary="Get user info"
)
def get_user(
  request: Request,
  jwt: str = Security(authorization_header),
  db: Session = Depends(create_connection)
):
  token = authorize_jwt(jwt)
  sub = get_sub(token)
  aud = get_aud(token)

  log.debug("Getting sv list. sub=\"{}\"".format(sub))

  if not check_role(aud, 'root:manage_user'):
    log.debug("User is not an admin. user_uid=\"{}\"".format(sub))
    raise HTTPException(status_code=403, detail='Forbidden')

  name = request.query_params.get('name')
  id = request.query_params.get('id')

  if name == '':
    name = None
  if id == '':
    id = None

  data = access_get_user(
    db,
    id=id,
    name=name,
  )

  return JSONResponse(
    content={
      'code': 200,
      'state': 'OK',
      'data': data
    }
  )
