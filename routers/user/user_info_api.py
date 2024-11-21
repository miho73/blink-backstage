import logging

from fastapi import APIRouter, Security, Depends, HTTPException
from starlette.responses import JSONResponse

from core.authentication.authorization_service import authorization_header, authorize_jwt
from core.user import user_info
from database.database import create_connection
from models.database_models import Identity, GoogleMethod, AuthLookup
from models.database_models.password_auth import PasswordMethod

log = logging.getLogger(__name__)

router = APIRouter(
  prefix='/api/user',
  tags=['user']
)


@router.get(
  path='/get'
)
def get_user(
  auth: str = Security(authorization_header),
  db=Depends(create_connection)
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


@router.get(
  path='/auth/get',
  tags=['authentication']
)
def get_auth_lookup(
  auth: str = Security(authorization_header),
  db=Depends(create_connection)
):
  log.debug('Query auth lookup upon JWT. jwt=\"{}\"'.format(auth))
  token = authorize_jwt(auth)

  sub = token.get("sub")

  identity: Identity = user_info.get_identity_by_userid(sub, db)
  if identity is None:
    log.debug('Identity was not found and auth lookup was not returned. user_uid=\"{}\"'.format(sub))
    raise HTTPException(status_code=400, detail="Identity not found")

  auth_lookup: AuthLookup = identity.auth_lookup

  google_auth = None
  password_auth = None

  if auth_lookup.google:
    google_method: GoogleMethod = auth_lookup.google_method
    google_auth = {
      "last_used": google_method.last_used.isoformat()
    }
  if auth_lookup.password:
    password_method: PasswordMethod = auth_lookup.password_method
    password_auth = {
      "last_used": password_method.last_used.isoformat(),
      "last_changed": password_method.last_changed.isoformat(),
      "id": password_method.user_id
    }

  return JSONResponse(
    content={
      "user_id": auth_lookup.user_id,
      "google": auth_lookup.google,
      "password": auth_lookup.password,
      "passkey": auth_lookup.passkey,
      "auth": {
        "google": google_auth,
        "password": password_auth
      }
    }
  )
