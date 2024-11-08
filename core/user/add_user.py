from sqlalchemy.orm import Session

from core.google.oauth import get_google_user
from models.database_models import GoogleMethod, Identity, AuthLookup
from models.request_models.RegisterRequests import GoogleRegisterRequest
from models.user import GoogleUser


def add_google_user(request: GoogleRegisterRequest, db: Session):
  google_user: GoogleUser = get_google_user(request.code)

  identity: Identity = Identity(
    username=request.username,

    email=google_user.email,
    email_verified=google_user.email_verified
  )

  auth_lookup: AuthLookup = AuthLookup(
    google=True,
    password=False,
    passkey=False,

    identity = identity
  )

  google_method: GoogleMethod = GoogleMethod(
    google_id=google_user.google_id,
    auth_lookup=auth_lookup
  )

  db.add(google_method)
