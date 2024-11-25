import logging

from fastapi import HTTPException
from sqlalchemy.orm import Session

from core.cryptography.bcrypt import hash_bcrypt
from core.google.google_oauth import get_google_user
from core.validation import validate_all, length_check, regex_check, assert_value
from models.database_models import GoogleMethod, Identity, AuthLookup
from models.database_models.password_auth import PasswordMethod
from models.request_models.register_requests import GoogleRegisterRequest, PasswordRegisterRequest
from models.user import GoogleUser

log = logging.getLogger(__name__)


def add_google_user(request: GoogleRegisterRequest, db: Session):
  google_user: GoogleUser = get_google_user(request.code)

  # form validation
  if validate_all(
    length_check(google_user.email, 5, 255),
    regex_check(google_user.email, r'^[-\w.]+@([\w-]+\.)+[\w-]{2,4}$'),
    assert_value(google_user.email_verified, True),
  ):
    log.debug("Form validation failed")
    raise HTTPException(status_code=400, detail="Form validation failed")

  identity: Identity = Identity(
    username=request.username,

    email=google_user.email,
    email_verified=google_user.email_verified
  )

  auth_lookup: AuthLookup = AuthLookup(
    google=True,
    password=False,
    passkey=False,

    identity=identity
  )

  google_method: GoogleMethod = GoogleMethod(
    google_id=google_user.google_id,
    auth_lookup=auth_lookup
  )

  db.add(google_method)
  log.debug("Added new google user to database. google_sub=\"{}\"".format(google_user.google_id))


def add_password_user(request: PasswordRegisterRequest, db: Session):
  pwd = hash_bcrypt(request.password)

  identity: Identity = Identity(
    username=request.username,
    email=request.email
  )

  auth_lookup: AuthLookup = AuthLookup(
    google=False,
    password=True,
    passkey=False,

    identity=identity
  )

  password_method: PasswordMethod = PasswordMethod(
    user_id=request.id,
    password=pwd,

    auth_lookup=auth_lookup
  )

  db.add(password_method)
