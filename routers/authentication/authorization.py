import logging

from fastapi import APIRouter, Security
from starlette.responses import JSONResponse

from core.authentication.authorization import authorization_header, authorize_jwt

log = logging.getLogger(__name__)

router = APIRouter(
  prefix='/api/auth/authorization',
  tags=['authorization']
)


@router.post(
  path=''
)
def authorize(
  auth: str = Security(authorization_header)
):
  log.debug("Authorizing user with JWT token. jwt: {token}".format(token=auth))
  authorize_jwt(auth)

  return JSONResponse(
    status_code=200,
    content={
      "code": 200,
      "state": "OK",
      "authorized": True
    }
  )
