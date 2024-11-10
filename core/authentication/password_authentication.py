import logging
from datetime import datetime
from typing import Optional

from core.cryptography import bcrypt
from core.google.recaptcha import location
from core.jwt import jwt
from models.database_models import Identity

log = logging.getLogger(__name__)

def password_authentication(identity: Identity, password: str) -> Optional[str]:
    stored_password = identity.auth_lookup.password_method.password

    if bcrypt.verify_bcrypt(password, stored_password):
      log.debug("Password authentication success. id=\"{}\"".format(identity.user_id))
      identity.last_login = datetime.now()
      identity.auth_lookup.password_method.last_used = datetime.now()

      log.debug("Issued JWT. user_id=\"{user_id}\", role=\"{role}\"".format(user_id=identity.user_id, role=identity.role))
      return jwt.create_token(identity.user_id, identity.role)

    else:
      log.debug("Password authentication failed. id=\"{}\"".format(identity.user_id))
      return None
