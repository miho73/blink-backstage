import logging

from fastapi import Request, APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from starlette.responses import RedirectResponse, JSONResponse

from core.authentication.auth_lookup_service import OAuthMethods, find_identity_from_auth_id
from core.config import config
from core.cryptography import aes256
from core.google.google_oauth_service import start_authentication, complete_google_authentication, get_google_sub, \
  get_access_token
from core.google.recaptcha_service import verify_recaptcha
from core.user.add_user_service import add_google_user
from database.database import create_connection
from models.request_models.register_requests import GoogleRegisterRequest

log = logging.getLogger(__name__)

router = APIRouter(
  prefix="/api/auth/google",
  tags=["google-authentication", "authentication"]
)


@router.get(
  path="/login",
  summary="Redirect request to Google OAuth2 signin",
)
def start_google_login_api():
  log.info("Redirecting to Google OAuth signin")
  auth_url, state = start_authentication()

  e_state = aes256.encrypt(state)
  log.debug("Generated state value. state=\"{state}\", estate=\"{estate}\"".format(state=state, estate=e_state))

  response = RedirectResponse(auth_url, 302)
  log.debug("Sent 302 Redirect. url=\"{url}\"".format(url=auth_url))
  response.set_cookie(
    key="blink-state",
    value=e_state,
    httponly=True,
    secure=config['env'] == "production",
    samesite="lax",
    path="/"
  )

  return response


@router.get(
  path="/callback",
  summary="Callback for Google OAuth2 signin",
)
def google_login_callback_api(
  request: Request,
  db: Session = Depends(create_connection)
):
  log.info("Handling Google OAuth2 callback")

  # check state
  e_cookie_state = request.cookies.get("blink-state")
  response_state = request.query_params.get("state")
  log.debug(
    "Checking state cookie and callback. cookie_state=\"{cookie_state}\", callback_state=\"{response_state}\"".format(
      cookie_state=e_cookie_state, response_state=response_state))

  if e_cookie_state is None or response_state is None:
    log.error("Callback or Cookie State is unset")
    return RedirectResponse("/auth?error=state-unset", 302)

  cookie_state = aes256.decrypt(e_cookie_state)
  log.debug("Decrypted cookie state. cookie_state=\"{cookie_state}\", callback_state=\"{response_state}\"".format(
    cookie_state=cookie_state, response_state=response_state))
  if cookie_state is None or cookie_state != response_state:
    log.error("States from cookie and callback does not match")
    return RedirectResponse("/auth?error=state-mismatch", 302)

  # check if user exists in google methods
  code = request.query_params.get("code")
  access_token = get_access_token(code)
  google_id: str = get_google_sub(access_token)
  identity = find_identity_from_auth_id(google_id, OAuthMethods.GOOGLE, db)

  if identity is None:
    log.info("User does not exist in Google Methods. Redirecting to registration. google_id=\"{}\"".format(google_id))
    return RedirectResponse(
      "/auth/register/google?code={}".format(access_token), 302)

  else:
    log.info("User exists in Google Methods. Redirecting to login. google_id=\"{}\"".format(google_id))
    jwt = complete_google_authentication(identity)
    db.commit()
    response = RedirectResponse("/auth/complete?jwt={jwt}".format(jwt=jwt), 302)
    response.delete_cookie("blink-state")
    return response


@router.post(
  path="/register",
  summary="Register new Google user",
)
def register_google_user_api(
  body: GoogleRegisterRequest,
  request: Request,
  db: Session = Depends(create_connection)
):
  log.debug("Registering Google User")

  # google recaptcha
  if verify_recaptcha(body.recaptcha, request.client.host, "signup/google") is False:
    log.error("Recaptcha school_verification failed")
    raise HTTPException(status_code=400, detail="Recaptcha failed")

  add_google_user(body, db)
  db.commit()

  response = JSONResponse(
    status_code=201,
    content={
      "code": 201,
      "state": "CREATED",
    }
  )
  response.delete_cookie("blink-state")
  return response
