import logging

from fastapi import APIRouter, Security, HTTPException, Request
from starlette.responses import JSONResponse

from core.authentication.authorization_service import authorization_header, authorize_jwt
from core.jwt.jwt_service import get_sub, get_aud
from core.school.neis_school_service import query_school_info
from core.user.user_info_service import check_role

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
  sub = get_sub(token)
  aud = get_aud(token)

  log.debug("Querying NEIS school data. sub=\"{}\"".format(sub))

  school_name = request.query_params.get('schoolName')

  if not check_role(aud, 'root:neis_api'):
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
