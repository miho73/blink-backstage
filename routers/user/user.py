import logging

from fastapi import APIRouter, Security, Depends, HTTPException
from starlette.responses import JSONResponse

from core.authentication.authorization import authorization_header, authorize_jwt
from core.user import user_info
from database.database import create_connection
from models.database_models import Identity

log = logging.getLogger(__name__)

router = APIRouter(
  prefix='/api/user',
  tags=['user']
)

@router.get(
  path = '/get'
)
def get_user(
  auth: str = Security(authorization_header),
  db = Depends(create_connection)
):
  log.debug("Getting user information upon JWT. jwt=\"{}\"".format(auth))
  token = authorize_jwt(auth)

  sub = token.get("sub")

  identity: Identity = user_info.get_identity_by_userid(sub, db)
  if identity is None:
    log.debug("Identity specified by JWT was not found. user_uid=\"{}\"".format(sub))
    raise HTTPException(status_code=400, detail="Identity not found")

  log.debug("User identity retrieved. user_role=\"{}\", ".format(identity.role))

  return JSONResponse(
    content={
      "user": {
        "role": identity.role.name,
        "user_id": identity.user_id,
        "email": identity.email,
        "emailVerified": identity.email_verified,
        "username": identity.username,
        "last_login": identity.last_login.isoformat(),
        "student_verified": identity.student_verified
      },
      "code": 200,
      "state": "OK"
    }
  )
