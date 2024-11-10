import logging

from fastapi import APIRouter, Request, HTTPException
from fastapi.params import Depends
from sqlalchemy.orm import Session
from starlette.responses import JSONResponse

from core.authentication.auth_lookup_service import find_identity, OAuthMethods
from core.authentication.password_authentication import password_authentication
from core.google.recaptcha import verify_recaptcha
from core.user.add_user import add_password_user
from core.validation import validate_all, length_check, length_check_min, regex_check
from database.database import create_connection
from models.request_models.RegisterRequests import PasswordRegisterRequest
from models.request_models.SigninModel import PasswordSigninRequest

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
    log.debug("Recaptcha verification failed")
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
  path = '/register'
)
def register_password_user(
  body: PasswordRegisterRequest,
  request: Request,
  db: Session = Depends(create_connection)
):
  log.debug("Registering Password User")

  # form validation
  if validate_all(
    length_check(body.username, 1, 100),
    length_check(body.email, 5, 255),
    regex_check(body.email, r'^[-.\w]+@([\w-]+\.)+[\w-]{2,4}$'),

    length_check(body.id, 1, 255),
    length_check_min(body.password, 6),

    body.recaptcha is not None
  ):
    log.debug("Form validation failed")
    raise HTTPException(status_code=400, detail="Form validation failed")

  # google recaptcha
  if verify_recaptcha(body.recaptcha, request.client.host, "signup/password") is False:
    log.debug("Recaptcha verification failed")
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

