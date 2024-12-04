import logging

from fastapi import APIRouter, Security, HTTPException, Request
from starlette.responses import JSONResponse

from core.authentication.authorization_service import authorization_header, authorize_jwt
from core.school.neis_school_service import query_school_info

log = logging.getLogger(__name__)

router = APIRouter(
  prefix='/api/school/neis',
  tags=['school', 'neis']
)


@router.get(
  path=''
)
def query_neis_school(
  request: Request,
  jwt: str = Security(authorization_header)
):
  token = authorize_jwt(jwt)
  sub = token.get('sub')
  aud = token.get('aud')

  log.debug("Querying NEIS school data. sub=\"{}\"".format(sub))

  school_name = request.query_params.get('schoolName')

  log.debug(aud)
  if 'blink:admin' not in aud:
    log.debug("User is not an admin. user_uid=\"{}\"".format(token.get('sub')))
    raise HTTPException(status_code=403, detail="Forbidden")

  if school_name is None:
    log.debug('School name was not given')
    raise HTTPException(status_code=400, detail='School name was not given')

  data = query_school_info(school_name)

  return JSONResponse(
    content={
      'code': 200,
      'state': 'OK',
      'data': data
    }
  )
