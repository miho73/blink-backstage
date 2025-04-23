import logging

from sqlalchemy import asc
from sqlalchemy.orm import Session

from models.database_models.relational.identity import Identity

log = logging.getLogger(__name__)


def access_get_user(db: Session, **kwargs):
  data = (
    db.query(Identity)
    .filter(
      Identity.username.like(
        kwargs.get('name') is not None and
        '%' + kwargs.get('name') + '%'
        or '%'
      )
    )
    .filter(
      kwargs.get('id') is not None and Identity.user_id.is_(kwargs.get('id')) or True
    )
    .order_by(asc(Identity.join_date))
    .limit(50)
    .all()
  )

  res = []

  for identity in data:
    res.append({
      "userId": str(identity.user_id),
      "username": identity.username,
      "email": identity.email,
      "emailVerified": identity.email_verified,
      "joinDate": identity.join_date.isoformat(),
      "lastLogin": identity.last_login.isoformat(),
      "grade": identity.grade,
      "classroom": identity.classroom,
      "studentNumber": identity.student_number,
      "role": identity.role,
    })

  return res
