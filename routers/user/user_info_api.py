import logging
from typing import Type

from fastapi import APIRouter, Security, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from starlette.responses import JSONResponse

from core.authentication.authorization_service import authorization_header, authorize_jwt
from core.google.recaptcha_service import verify_recaptcha
from core.user import user_info_service
from core.user.user_info_service import update_user_profile, role_to_school
from database.database import create_connection
from models.database_models.relational.auth_lookup import AuthLookup
from models.database_models.relational.google_auth import GoogleAuth
from models.database_models.relational.identity import Identity
from models.database_models.relational.passkey_auth import PasskeyAuth
from models.database_models.relational.password_auth import PasswordAuth
from models.database_models.relational.schools import School
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
  token = authorize_jwt(auth)
  sub = token.get("sub")

  log.debug("Getting user information. sub=\"{}\"".format(sub))

  identity: Identity = user_info_service.get_identity_by_userid(sub, db)
  if identity is None:
    log.debug("Identity specified by JWT was not found. user_uid=\"{}\"".format(sub))
    raise HTTPException(status_code=400, detail="Identity not found")

  log.debug("User identity retrieved. user_role=\"{}\", ".format(identity.role))
  return JSONResponse(
    content={
      "user": {
        "role": identity.role,
        "userId": str(identity.user_id),
        "email": identity.email,
        "emailVerified": identity.email_verified,
        "username": identity.username,
        "lastLogin": identity.last_login.isoformat(),
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
  token = authorize_jwt(auth)
  sub = token.get("sub")

  log.debug('Query auth lookup. sub=\"{}\"'.format(sub))

  identity: Identity = user_info_service.get_identity_by_userid(sub, db)
  if identity is None:
    log.debug('Identity was not found and auth lookup was not returned. user_uid=\"{}\"'.format(sub))
    raise HTTPException(status_code=400, detail="Identity not found")

  auth_lookup: AuthLookup = identity.auth_lookup

  auth_config: dict = {}

  google_auth: GoogleAuth
  password_auth: PasswordAuth

  if auth_lookup.google:
    google_auth: GoogleAuth = auth_lookup.google_auth
    auth_config['google'] = {
      "last_used": google_auth.last_used.isoformat()
    }
  if auth_lookup.password:
    password_method: PasswordAuth = auth_lookup.password_auth
    auth_config['password'] = {
      "last_used": password_method.last_used.isoformat(),
      "last_changed": password_method.last_changed.isoformat(),
      "id": password_method.user_id
    }
  if auth_lookup.passkey >= 1:
    passkeys: list[PasskeyAuth] = auth_lookup.passkey_auth
    passkey_config = []

    for passkey in passkeys:
      passkey_config.append({
        "lastUsed": passkey.last_used.isoformat() if passkey.last_used is not None else None,
        "name": passkey.passkey_name,
        "aaguid": passkey.aaguid,
        "createdAt": passkey.created_at.isoformat(),
        "passkeyId": str(passkey.passkey_id)
      })

    auth_config['passkey'] = passkey_config

  return JSONResponse(
    content={
      "userId": str(auth_lookup.user_id),
      "google": auth_lookup.google,
      "password": auth_lookup.password,
      "passkey": auth_lookup.passkey,
      "auth": auth_config
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
  token = authorize_jwt(auth)
  sub = token.get("sub")

  log.debug("Getting school school_verification data. sub=\"{}\"".format(sub))

  identity: Type[Identity] = user_info_service.get_identity_by_userid(sub, db)
  if identity is None:
    log.debug("Identity specified by JWT was not found. user_uid=\"{}\"".format(sub))
    raise HTTPException(status_code=400, detail="Identity not found")

  student_verified, neis_code = role_to_school(identity.role)

  if not student_verified:
    log.debug("User is not a student. user_uid=\"{}\"".format(sub))
    return JSONResponse(
      content={
        'verified': False,
        'school': None
      }
    )

  school = db.query(School).filter_by(neis_code=neis_code).first()

  if school is None:
    log.debug("School information is missing. user_uid=\"{}\"".format(sub))
    raise HTTPException(status_code=400, detail="School information is missing")

  if student_verified:
    school = {
      "name": school.school_name,
      "schoolUUID": str(school.school_id),
      "neisCode": school.neis_code,
      "grade": identity.grade
    }
  else:
    school = None

  return JSONResponse(
    content={
      'verified': True,
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
