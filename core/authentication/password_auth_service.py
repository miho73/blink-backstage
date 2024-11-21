import logging
from datetime import datetime
from typing import Optional

from fastapi import HTTPException

from core.cryptography import bcrypt
from core.jwt import jwt
from models.database_models import Identity
from models.database_models.password_auth import PasswordMethod

log = logging.getLogger(__name__)


def auth_with_password(identity: Identity, password: str) -> Optional[str]:
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


def change_password(identity: Identity, current_password: str, password: str):
  password_method: PasswordMethod = identity.auth_lookup.password_method

  # check current password
  if not bcrypt.verify_bcrypt(current_password, password_method.password):
    log.debug("Password mismatch and therefore it won't be changed")
    raise HTTPException(status_code=400, detail='Password mismatch')

  password_method.password = bcrypt.hash_bcrypt(password)
  password_method.last_changed = datetime.now()
  log.debug("Password was changed. id=\"{}\", user_uid=\"{}\"".format(password_method.user_id, identity.user_id))
