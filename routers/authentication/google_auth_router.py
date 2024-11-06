import logging

from fastapi import Request, APIRouter, Depends
from sqlalchemy.orm import Session
from starlette.responses import RedirectResponse

from core.config import config
from core.cryptography import aes256
from core.google.oauth import start_authentication, complete_oauth_flow
from database.database import create_connection

log = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/auth/google",
    tags=["google", "authentication"]
)

@router.get(
  path="/web/begin"
)
def start_google_login():
  log.info("Redirecting to Google OAuth signin")
  auth_url, state = start_authentication()

  e_state = aes256.encrypt(state)
  log.debug("Generated state value. state=\"{state}\", estate=\"{estate}\"".format(state=state, estate=e_state))

  response = RedirectResponse(auth_url, 302)
  log.debug("Sent 302 Redirect. url=\"{url}\"".format(url=auth_url))
  response.set_cookie(
    key="with-state",
    value=e_state,
    httponly=True,
    secure=config['env'] == "production",
    samesite="lax",
    path="/"
  )

  return response

@router.get(
  path="/web/callback"
)
def complete_google_login(request: Request, db: Session = Depends(create_connection)):
  log.info("Handling Google OAuth2 Callback")

  if request.query_params.get("error"):
    log.error(
      "Google OAuth2 signin returned an error. error=\"{error}\"".format(error=request.query_params.get("error")))
    return RedirectResponse("/auth?error=google_error", 302)

  # check state
  e_cookie_state = request.cookies.get("with-state")
  response_state = request.query_params.get("state")
  log.debug(
    "Checking state cookie and callback. cookie_state=\"{cookie_state}\", callback_state=\"{response_state}\"".format(
      cookie_state=e_cookie_state, response_state=response_state))

  if e_cookie_state is None or response_state is None:
    log.error("Callback or Cookie State is unset")
    return RedirectResponse("/auth?error=state_unset", 302)

  cookie_state = aes256.decrypt(e_cookie_state)
  log.debug("Decrypted cookie state. cookie_state=\"{cookie_state}\", callback_state=\"{response_state}\"".format(
    cookie_state=cookie_state, response_state=response_state))
  if cookie_state is None or cookie_state != response_state:
    log.error("States from cookie and callback does not match")
    return RedirectResponse("/auth?error=state_mismatch", 302)

  # check code
  code = request.query_params.get("code")
  if code is None:
    log.error("Code from callback is not set")
    return RedirectResponse("/auth?error=code_unset", 302)

  try:
    log.debug("Complete Google OAuth flow. oauth2_code=\"{code}\"".format(code=code))
    jwt = complete_oauth_flow(code, db)
    db.commit()
  except Exception as e:
    log.error("Internal Server Error: {error}".format(error=str(e)), exc_info=e)
    return RedirectResponse("/auth?error=internal_server_error", 302)

  log.debug("Redirecting to frontend with JWT token. jwt=\"{jwt}\"".format(jwt=jwt))
  response = RedirectResponse("/auth/complete?jwt={jwt}".format(jwt=jwt), 302)
  response.delete_cookie('with-state')

  return response
