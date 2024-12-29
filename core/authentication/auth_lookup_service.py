from enum import Enum
from typing import Optional

from sqlalchemy.orm import Session

from models.database_models.relational.google_auth import GoogleAuth
from models.database_models.relational.identity import Identity
from models.database_models.relational.password_auth import PasswordAuth


class OAuthMethods(Enum):
  GOOGLE = "google"
  PASSWORD = "password"
  PASSKEY = "passkey"


def find_identity_from_auth_id(identifier: str, provider: OAuthMethods, db: Session) -> Optional[Identity]:
  if provider == OAuthMethods.GOOGLE:
    google_auth = db.query(GoogleAuth).filter(GoogleAuth.google_id == identifier).first()

    if google_auth is None:
      return None

    return google_auth.auth_lookup.identity

  elif provider == OAuthMethods.PASSWORD:
    password_auth = db.query(PasswordAuth).filter(PasswordAuth.user_id == identifier).first()

    if password_auth is None:
      return None

    return password_auth.auth_lookup.identity
