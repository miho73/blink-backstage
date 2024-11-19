from sqlalchemy.orm import Session

from models.database_models import Identity


def get_identity_by_userid(user_id: int, db: Session):
  identity = db.query(Identity).filter(Identity.user_id == user_id).first()

  if identity is None:
    return None

  return identity
