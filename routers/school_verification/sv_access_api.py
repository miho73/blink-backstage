import logging

from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.params import Security
from sqlalchemy.orm import Session
from starlette.responses import JSONResponse

from core.authentication.authorization_service import authorization_header, authorize_jwt
from core.sv.sv_access_service import access_get_sv
from database.database import create_connection

log = logging.getLogger(__name__)

router = APIRouter(
  prefix='/api/sv/access',
  tags=['sv', 'access api']
)


@router.get(
  path=''
)
def get_sv_list(
  request: Request,
  jwt: str = Security(authorization_header),
  db: Session = Depends(create_connection)
):
  log.debug("Getting sv list upon JWT. jwt=\"{}\"".format(jwt))

  token = authorize_jwt(jwt)
  sub = token.get('sub')
  aud = token.get('aud')

  if 'blink:admin' not in aud:
    log.debug("User is not an admin. user_uid=\"{}\"".format(sub))
    raise HTTPException(status_code=403, detail='Forbidden')

  name = request.query_params.get('name')
  school_name = request.query_params.get('schoolName')

  if name == '':
    name = None
  if school_name == '':
    school_name = None

  data = access_get_sv(
    db,
    name=name,
    school_name=school_name
  )

  return JSONResponse(
    content={
      'code': 200,
      'state': 'OK',
      'data': data
    }
  )