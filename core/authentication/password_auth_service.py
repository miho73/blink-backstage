import logging
from datetime import datetime
from typing import Optional

from fastapi import HTTPException

from core.cryptography import bcrypt
from core.jwt import jwt_service
from models.database_models.relational.identity import Identity
from models.database_models.relational.password_auth import PasswordAuth

log = logging.getLogger(__name__)


def login_with_password(identity: Identity, password: str) -> Optional[str]:
  stored_password = identity.auth_lookup.password_auth.password

  if bcrypt.verify_bcrypt(password, stored_password):
    log.debug("Password authentication success. id=\"{}\"".format(identity.user_id))
    identity.last_login = datetime.now()
    identity.auth_lookup.password_auth.last_used = datetime.now()

    log.debug("Issued JWT. user_id=\"{user_id}\", role=\"{role}\"".format(user_id=identity.user_id, role=identity.role))
    return jwt_service.create_token(identity.user_id, identity.role)

  else:
    log.debug("Password authentication failed. id=\"{}\"".format(identity.user_id))
    return None


def update_password(identity: Identity, current_password: str, password: str):
  password_method: PasswordAuth = identity.auth_lookup.password_auth

  # check current password
  if not bcrypt.verify_bcrypt(current_password, password_method.password):
    log.debug("Password mismatch and therefore it won't be changed")
    raise HTTPException(status_code=400, detail='Password mismatch')

  password_method.password = bcrypt.hash_bcrypt(password)
  password_method.last_changed = datetime.now()
  log.debug("Password was changed. id=\"{}\", user_uid=\"{}\"".format(password_method.user_id, identity.user_id))
