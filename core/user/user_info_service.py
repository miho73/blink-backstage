import logging
from typing import Type

from fastapi import HTTPException
from sqlalchemy.orm import Session

from models.database_models.relational.identity import Identity
from models.request_models.user_requests import UpdateUserProfileRequest

log = logging.getLogger(__name__)

def get_identity_by_userid(user_id: int, db: Session) -> Type[Identity] | None:
  identity = db.query(Identity).filter(Identity.user_id == user_id).first()

  if identity is None:
    return None

  return identity

def update_user_profile(uid: int, request: UpdateUserProfileRequest, db: Session):
  identity = get_identity_by_userid(uid, db)

  if identity is None:
    log.debug("Identity specified by JWT was not found. user_uid=\"{}\"".format(uid))
    raise HTTPException(status_code=400, detail="Identity not found")

  current_identity = (
    db.query(Identity)
      .filter_by(user_id=uid)
      .first()
  )

  if current_identity.email != request.email:
    log.debug('Email was changed. email verification set to false. user_uid="{}", email="{}"'.format(uid, request.email))
    current_identity.email_verified = False
    current_identity.email = request.email

  current_identity.username = request.username

  db.commit()
