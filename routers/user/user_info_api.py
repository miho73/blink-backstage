import logging

from fastapi import APIRouter, Security, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from starlette.responses import JSONResponse

from core.authentication.authorization_service import authorization_header, authorize_jwt
from core.google.recaptcha_service import verify_recaptcha
from core.user import user_info_service
from core.user.user_info_service import update_user_profile
from database.database import create_connection
from models.database_models import Identity, GoogleMethod, AuthLookup
from models.database_models.password_auth import PasswordMethod
from models.request_models.user_requests import UpdateUserProfileRequest

log = logging.getLogger(__name__)

router = APIRouter(
  prefix='/api/user',
  tags=['user']
)


@router.get(
  path='',
  summary="Get user information",
)
def get_user_api(
  auth: str = Security(authorization_header),
  db=Depends(create_connection)
):
  log.debug("Getting user information upon JWT. jwt=\"{}\"".format(auth))
  token = authorize_jwt(auth)

  sub = token.get("sub")

  identity: Identity = user_info_service.get_identity_by_userid(sub, db)
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
  path='/auth',
  tags=['authentication'],
  summary="Get user authentication information",
)
def get_auth_lookup_api(
  auth: str = Security(authorization_header),
  db=Depends(create_connection)
):
  log.debug('Query auth lookup upon JWT. jwt=\"{}\"'.format(auth))
  token = authorize_jwt(auth)

  sub = token.get("sub")

  identity: Identity = user_info_service.get_identity_by_userid(sub, db)
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

@router.get(
  path='/sv',
  tags=['sv'],
  summary="Get school verification information",
)
def get_verification_info_api(
  auth: str = Security(authorization_header),
  db: Session = Depends(create_connection)
):
  log.debug("Getting school school_verification data upon JWT. jwt=\"{}\"".format(auth))

  token = authorize_jwt(auth)
  sub = token.get("sub")

  identity: Identity = user_info_service.get_identity_by_userid(sub, db)
  if identity is None:
    log.debug("Identity specified by JWT was not found. user_uid=\"{}\"".format(sub))
    raise HTTPException(status_code=400, detail="Identity not found")

  if identity.student_verified:
    school = {
      "name": identity.school.school_name,
      "id": identity.school.school_id,
      "grade": identity.grade
    }
  else:
    school = None

  return JSONResponse(
    content={
      'verified': identity.student_verified,
      'school': school
    }
  )

@router.patch(
  path='',
  summary="Update user information",
)
def update_user_api(
  body: UpdateUserProfileRequest,
  request: Request,
  jwt: str = Security(authorization_header),
  db: Session = Depends(create_connection)
):
  token = authorize_jwt(jwt)
  sub = token.get("sub")

  log.debug("Updating user information. user_uid=\"{}\"".format(sub))

  if verify_recaptcha(body.recaptcha, request.client.host, "profile/update") is False:
    log.debug("Recaptcha verification failed. user_uid=\"{}\"".format(sub))
    raise HTTPException(status_code=400, detail="Recaptcha verification failed")

  update_user_profile(sub, body, db)
  log.debug("User information updated. user_uid=\"{}\"".format(sub))

  return JSONResponse(
    content={
      "code": 200,
      "state": "OK"
    }
  )
