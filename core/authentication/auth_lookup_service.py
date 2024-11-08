from enum import Enum
from typing import Optional

from sqlalchemy.orm import Session

from models.database_models.google_method import GoogleMethod
from models.database_models.identity import Identity


class OAuthMethods(Enum):
  GOOGLE = "google"
  PASSWORD = "password"
  PASSKEY = "passkey"


def find_identity(identifier: str, provider: OAuthMethods, db: Session) -> Optional[Identity]:
  if provider == OAuthMethods.GOOGLE:
    google_auth: Optional[GoogleMethod] = db.query(GoogleMethod).filter(GoogleMethod.google_id == identifier).first()

    if google_auth is None:
      return None

    return google_auth.auth_lookup.identity
