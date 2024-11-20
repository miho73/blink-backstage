import logging

from fastapi import APIRouter, Request, HTTPException
from fastapi.params import Depends, Security
from sqlalchemy.orm import Session
from starlette.responses import JSONResponse

from core.authentication.auth_lookup_service import find_identity, OAuthMethods
from core.authentication.authorization import authorization_header, authorize_jwt
from core.authentication.password_authentication import password_authentication, change_password
from core.google.recaptcha import verify_recaptcha
from core.user import user_info
from core.user.add_user import add_password_user
from database.database import create_connection
from models.database_models import Identity
from models.request_models.signin_models import PasswordSigninRequest
from models.request_models.password_request import UpdatePasswordRequest
from models.request_models.register_request import PasswordRegisterRequest

log = logging.getLogger(__name__)

router = APIRouter(
  prefix='/api/auth/password',
  tags=['password']
)


@router.post(
  path='/signin'
)
def sign_in_password_user(
  body: PasswordSigninRequest,
  request: Request,
  db: Session = Depends(create_connection)
):
  log.debug("Signing in Password User. id=\"{}\"".format(body.id))

  # google recaptcha
  if verify_recaptcha(body.recaptcha, request.client.host, "signin/password") is False:
    log.debug("Recaptcha school_verification failed")
    raise HTTPException(status_code=400, detail="Recaptcha failed")

  # signin
  identity = find_identity(body.id, OAuthMethods.PASSWORD, db)
  if identity is None:
    log.debug("Identity not found. Signin was failed id=\"{}\"".format(body.id))
    raise HTTPException(status_code=401, detail="Bad credential")

  jwt = password_authentication(identity, body.password)
  db.commit()
  if jwt is None:
    log.debug("Password authentication failed. id=\"{}\"".format(body.id))
    raise HTTPException(status_code=401, detail="Bad credential")
  else:
    log.debug("Password authentication completed and succeed. id=\"{}\"".format(body.id))
    return JSONResponse(
      status_code=200,
      content={
        "code": 200,
        "state": "OK",
        "jwt": jwt
      }
    )


@router.post(
  path='/register'
)
def register_password_user(
  body: PasswordRegisterRequest,
  request: Request,
  db: Session = Depends(create_connection)
):
  log.debug("Registering Password User")

  # google recaptcha
  if verify_recaptcha(body.recaptcha, request.client.host, "signup/password") is False:
    log.debug("Recaptcha school_verification failed")
    raise HTTPException(status_code=400, detail="Recaptcha failed")

  add_password_user(body, db)
  db.commit()
  log.debug("Commited new password user to database. email=\"{}\", id=\"{}\"".format(body.email, body.id))

  response = JSONResponse(
    status_code=201,
    content={
      "code": 201,
      "state": "CREATED",
    }
  )
  return response


@router.patch(
  path='/update'
)
def update_password(
  body: UpdatePasswordRequest,
  request: Request,
  auth: str = Security(authorization_header),
  db: Session = Depends(create_connection)
):
  log.debug('Change password upon JWT. jwt=\"{}\"'.format(auth))

  if verify_recaptcha(body.recaptcha, request.client.host, 'changePassword') is False:
    log.debug("Recaptcha school_verification failed")
    raise HTTPException(status_code=400, detail="Recaptcha failed")

  token = authorize_jwt(auth)
  sub = token.get("sub")

  identity: Identity = user_info.get_identity_by_userid(sub, db)
  if identity is None:
    log.debug("Identity specified by JWT was not found. user_uid=\"{}\"".format(sub))
    raise HTTPException(status_code=400, detail="Identity not found")

  change_password(identity, body.current_password, body.new_password)
  db.commit()

  return JSONResponse(
    content={
      "code": 200,
      "state": "OK"
    }
  )
