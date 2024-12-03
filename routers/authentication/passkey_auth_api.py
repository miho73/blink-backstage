import logging
from typing import Annotated

from fastapi import APIRouter, Security, Request, HTTPException
from fastapi.params import Depends, Cookie
from sqlalchemy.orm import Session
from starlette.responses import JSONResponse

from core.authentication import passkey
from core.authentication.authorization_service import authorization_header, authorize_jwt
from core.config import config
from core.google.recaptcha_service import verify_recaptcha
from core.user import user_info_service
from database.database import create_connection
from models.request_models.passkey_request import RegisterPasskeyRequest, SignInPasskeyRequest

log = logging.getLogger(__name__)

router = APIRouter(
  prefix='/api/auth/passkey',
  tags=['authentication', 'passkey-authentication']
)

@router.get(
  path='/auth-option',
  summary="Get webauthn authentication options",
)
def get_auth_option_api():
  log.debug("User requested authentication option")

  (session_id, option) = passkey.begin_authentication()

  response = JSONResponse(
    content={
      'code': 200,
      'state': 'OK',
      'option': option
    }
  )
  response.set_cookie(
    key='PSK_AUTH_SEK',
    value=session_id,
    httponly=True,
    max_age=300,
    secure=config['session']['secure'],
    samesite='strict'
  )

  return response

@router.post(
  path='/login',
  summary="Login with webauthn passkey",
)
def login_passkey_api(
  body: SignInPasskeyRequest,
  PSK_AUTH_SEK: Annotated[str | None, Cookie()],
  request: Request,
  db: Session = Depends(create_connection)
):
  log.debug("Processing passkey login")

  if PSK_AUTH_SEK is None:
    log.debug("Passkey auth session not found")
    raise HTTPException(status_code=400, detail="Session not found")

  if verify_recaptcha(body.recaptcha, request.client.host, 'signin/passkey') is False:
    log.debug("Recaptcha verification failed")
    raise HTTPException(status_code=400, detail="Recaptcha verification failed")

  jwt = passkey.auth_passkey(body, PSK_AUTH_SEK, db)

  return JSONResponse(
    content={
      'code': 200,
      'state': 'OK',
      'jwt': jwt
    }
  )

@router.get(
  path='/register-option',
  summary="Get webauthn registration options",
)
def get_register_option_api(
  jwt: str = Security(authorization_header),
  db: Session = Depends(create_connection),
):
  token = authorize_jwt(jwt)
  sub = token.get("sub")

  identity = user_info_service.get_identity_by_userid(sub, db)

  if identity is None:
    log.debug("Identity not found. user_uid=\"{}\"".format(sub))
    raise HTTPException(status_code=404, detail="Identity not found")

  log.debug("User requested registration option. user_uid=\"{}\"".format(sub))
  (session_id, option) = passkey.begin_registration(identity)
  response = JSONResponse(
    content={
      'code': 200,
      'state': 'OK',
      'option': option
    },
  )
  response.set_cookie(
    key='PSK_REG_SEK',
    value=session_id,
    httponly=True,
    max_age=300,
    secure=config['session']['secure'],
    samesite='strict'
  )
  return response

@router.post(
  path='/register',
  summary="Register webauthn passkey credential",
)
def register_passkey_api(
  body: RegisterPasskeyRequest,
  PSK_REG_SEK: Annotated[str | None, Cookie()],
  request: Request,
  jwt: str = Security(authorization_header),
  db: Session = Depends(create_connection)
):
  token = authorize_jwt(jwt)
  sub = token.get("sub")

  log.debug("User requested passkey registration. user_uid=\"{}\"".format(sub))

  if PSK_REG_SEK is None:
    log.debug("Passkey register Session not found. user_uid=\"{}\"".format(sub))
    raise HTTPException(status_code=400, detail="Session not found")

  if verify_recaptcha(body.recaptcha, request.client.host, 'register/passkey') is False:
    log.debug("Recaptcha verification failed. user_uid=\"{}\"".format(sub))
    raise HTTPException(status_code=400, detail="Recaptcha verification failed")

  passkey.add_passkey(sub, body, PSK_REG_SEK, db)

  return JSONResponse(
    content={
      'code': 200,
      'state': 'OK'
    }
  )

@router.get(
  path='/aaguid/{theme}/{aaguid}',
  summary="Get authenticator icon by aaguid",
)
def get_authenticator(
  aaguid: str
):
  authenticator = passkey.get_authenticator(aaguid)
  if authenticator is None:
    log.debug("Authenticator not found. aaguid=\"{}\"".format(aaguid))
    raise HTTPException(status_code=404, detail="Authenticator not found")

  return JSONResponse(
    content={
      'code': 200,
      'state': 'OK',
      'icon': {
        'light': authenticator.icon_light,
        'dark': authenticator.icon_dark
      }
    }
  )
